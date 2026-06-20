from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shutil
from typing import Any


@dataclass(frozen=True)
class ItemDef:
    id: str
    display_name: str | None = None
    max_stack_size: int = 64
    texture: str | None = None
    texture_file: str | None = None


@dataclass(frozen=True)
class BlockDef:
    id: str
    display_name: str | None = None
    hardness: float = 1.5
    resistance: float = 6.0
    needs_block_item: bool = True
    max_stack_size: int = 64
    texture: str | None = None
    texture_file: str | None = None
    textures: dict[str, str] | None = None
    texture_files: dict[str, str] | None = None


@dataclass(frozen=True)
class CreativeTabDef:
    id: str
    display_name: str
    icon: str
    entries: list[str]


@dataclass(frozen=True)
class ShapedRecipeDef:
    id: str
    result: str
    pattern: list[str]
    key: dict[str, str]
    count: int = 1
    category: str = "misc"


@dataclass(frozen=True)
class ShapelessRecipeDef:
    id: str
    result: str
    ingredients: list[str]
    count: int = 1
    category: str = "misc"


@dataclass
class ModConfig:
    minecraft_version: str | None = None


_items: list[ItemDef] = []
_blocks: list[BlockDef] = []
_creative_tabs: list[CreativeTabDef] = []
_shaped_recipes: list[ShapedRecipeDef] = []
_shapeless_recipes: list[ShapelessRecipeDef] = []
_config = ModConfig()


def clear() -> None:
    _items.clear()
    _blocks.clear()
    _creative_tabs.clear()
    _shaped_recipes.clear()
    _shapeless_recipes.clear()
    _config.minecraft_version = None


def config(*, mod_version: int | str | None = None, minecraft_version: int | str | None = None) -> ModConfig:
    if mod_version is not None and minecraft_version is not None:
        raise ValueError("use either mod_version or minecraft_version, not both")

    version = minecraft_version if minecraft_version is not None else mod_version
    if version is not None:
        _config.minecraft_version = normalize_minecraft_version(version)

    return _config


def item(
    id: str,
    *,
    display_name: str | None = None,
    max_stack_size: int = 64,
    texture: str | None = None,
    texture_file: str | Path | None = None,
) -> ItemDef:
    _validate_id(id)
    _ensure_can_register_item(id)
    _ensure_one_texture_source(texture=texture, texture_file=texture_file)
    _validate_stack_size(max_stack_size)

    definition = ItemDef(
        id=id,
        display_name=display_name,
        max_stack_size=max_stack_size,
        texture=texture,
        texture_file=str(texture_file) if texture_file is not None else None,
    )
    _items.append(definition)
    return definition


def block(
    id: str,
    *,
    display_name: str | None = None,
    hardness: float = 1.5,
    resistance: float = 6.0,
    needs_block_item: bool = True,
    max_stack_size: int = 64,
    texture: str | None = None,
    texture_file: str | Path | None = None,
    textures: dict[str, str] | None = None,
    texture_files: dict[str, str | Path] | None = None,
) -> BlockDef:
    _validate_id(id)
    _ensure_can_register_block(id, needs_block_item=needs_block_item)
    _ensure_one_block_texture_source(
        texture=texture,
        texture_file=texture_file,
        textures=textures,
        texture_files=texture_files,
    )
    if hardness < 0:
        raise ValueError("hardness must be 0 or greater")
    if resistance < 0:
        raise ValueError("resistance must be 0 or greater")
    _validate_stack_size(max_stack_size)
    normalized_textures = _normalize_face_texture_refs(textures) if textures is not None else None
    normalized_texture_files = _normalize_face_texture_files(texture_files) if texture_files is not None else None

    definition = BlockDef(
        id=id,
        display_name=display_name,
        hardness=hardness,
        resistance=resistance,
        needs_block_item=needs_block_item,
        max_stack_size=max_stack_size,
        texture=texture,
        texture_file=str(texture_file) if texture_file is not None else None,
        textures=normalized_textures,
        texture_files=normalized_texture_files,
    )
    _blocks.append(definition)
    return definition


def creative_tab(
    id: str,
    *,
    display_name: str,
    icon: str,
    entries: list[str] | tuple[str, ...],
) -> CreativeTabDef:
    _validate_id(id)
    if any(definition.id == id for definition in _creative_tabs):
        raise ValueError(f"duplicate creative tab id: {id!r}")
    if not entries:
        raise ValueError("creative tab entries cannot be empty")

    entry_list = [normalize_ref(entry) for entry in entries]
    definition = CreativeTabDef(
        id=id,
        display_name=display_name,
        icon=normalize_ref(icon),
        entries=entry_list,
    )
    _creative_tabs.append(definition)
    return definition


def shaped_recipe(
    id: str,
    *,
    result: str,
    pattern: list[str] | tuple[str, ...],
    key: dict[str, str],
    count: int = 1,
    category: str = "misc",
) -> ShapedRecipeDef:
    _validate_id(id)
    _ensure_recipe_id_available(id)
    _validate_count(count)
    pattern_list = list(pattern)
    _validate_pattern(pattern_list, key)
    definition = ShapedRecipeDef(
        id=id,
        result=normalize_ref(result),
        pattern=pattern_list,
        key={symbol: normalize_ref(value) for symbol, value in key.items()},
        count=count,
        category=category,
    )
    _shaped_recipes.append(definition)
    return definition


def shapeless_recipe(
    id: str,
    *,
    result: str,
    ingredients: list[str] | tuple[str, ...],
    count: int = 1,
    category: str = "misc",
) -> ShapelessRecipeDef:
    _validate_id(id)
    _ensure_recipe_id_available(id)
    _validate_count(count)
    if not ingredients:
        raise ValueError("shapeless recipe ingredients cannot be empty")

    definition = ShapelessRecipeDef(
        id=id,
        result=normalize_ref(result),
        ingredients=[normalize_ref(ingredient) for ingredient in ingredients],
        count=count,
        category=category,
    )
    _shapeless_recipes.append(definition)
    return definition


def build(*, mod_id: str, resources_dir: str | Path, mod_version: int | str | None = None) -> Path:
    _validate_id(mod_id)
    if mod_version is not None:
        config(mod_version=mod_version)

    resources_path = Path(resources_dir)
    data_path = resources_path / "assets" / mod_id / "pyneoforge" / "generated.json"
    lang_path = resources_path / "assets" / mod_id / "lang" / "en_us.json"

    data_path.parent.mkdir(parents=True, exist_ok=True)
    lang_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema": 1,
        "minecraft_version": _config.minecraft_version,
        "items": [asdict(definition) for definition in _items],
        "blocks": [asdict(definition) for definition in _blocks],
        "creative_tabs": [asdict(definition) for definition in _creative_tabs],
    }
    data_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lang = _language_entries(mod_id)
    lang_path.write_text(json.dumps(lang, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_model_resources(resources_path=resources_path, mod_id=mod_id)
    _write_recipe_resources(resources_path=resources_path, mod_id=mod_id)
    _copy_texture_files(resources_path=resources_path, mod_id=mod_id)

    return data_path


def _language_entries(mod_id: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for definition in _items:
        if definition.display_name:
            entries[f"item.{mod_id}.{definition.id}"] = definition.display_name
    for definition in _blocks:
        if definition.display_name:
            entries[f"block.{mod_id}.{definition.id}"] = definition.display_name
    for definition in _creative_tabs:
        entries[f"itemGroup.{mod_id}.{definition.id}"] = definition.display_name
    return entries


def _write_model_resources(*, resources_path: Path, mod_id: str) -> None:
    for definition in _items:
        _write_json(
            resources_path / "assets" / mod_id / "models" / "item" / f"{definition.id}.json",
            {
                "parent": "minecraft:item/generated",
                "textures": {"layer0": _texture_ref(mod_id, "item", definition)},
            },
        )

    for definition in _blocks:
        _write_json(
            resources_path / "assets" / mod_id / "blockstates" / f"{definition.id}.json",
            {
                "variants": {
                    "": {"model": f"{mod_id}:block/{definition.id}"},
                },
            },
        )
        _write_json(
            resources_path / "assets" / mod_id / "models" / "block" / f"{definition.id}.json",
            _block_model_json(mod_id, definition),
        )
        if definition.needs_block_item:
            _write_json(
                resources_path / "assets" / mod_id / "models" / "item" / f"{definition.id}.json",
                {"parent": f"{mod_id}:block/{definition.id}"},
            )


def _write_recipe_resources(*, resources_path: Path, mod_id: str) -> None:
    for definition in _shaped_recipes:
        _write_json(
            resources_path / "data" / mod_id / "recipe" / f"{definition.id}.json",
            {
                "type": "minecraft:crafting_shaped",
                "category": definition.category,
                "pattern": definition.pattern,
                "key": {
                    symbol: _ingredient_json(ref, mod_id)
                    for symbol, ref in definition.key.items()
                },
                "result": _result_json(definition.result, definition.count, mod_id),
            },
        )

    for definition in _shapeless_recipes:
        _write_json(
            resources_path / "data" / mod_id / "recipe" / f"{definition.id}.json",
            {
                "type": "minecraft:crafting_shapeless",
                "category": definition.category,
                "ingredients": [
                    _ingredient_json(ingredient, mod_id)
                    for ingredient in definition.ingredients
                ],
                "result": _result_json(definition.result, definition.count, mod_id),
            },
        )


def _copy_texture_files(*, resources_path: Path, mod_id: str) -> None:
    for definition in _items:
        if definition.texture_file:
            _copy_texture_file(
                source=definition.texture_file,
                destination=resources_path
                / "assets"
                / mod_id
                / "textures"
                / "item"
                / f"{definition.id}.png",
            )

    for definition in _blocks:
        if definition.texture_files:
            for face, source in definition.texture_files.items():
                _copy_texture_file(
                    source=source,
                    destination=resources_path
                    / "assets"
                    / mod_id
                    / "textures"
                    / "block"
                    / definition.id
                    / f"{face}.png",
                )
        elif definition.texture_file:
            _copy_texture_file(
                source=definition.texture_file,
                destination=resources_path
                / "assets"
                / mod_id
                / "textures"
                / "block"
                / f"{definition.id}.png",
            )


def _copy_texture_file(*, source: str, destination: Path) -> None:
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"texture file does not exist: {source}")
    if source_path.suffix.lower() != ".png":
        raise ValueError(f"texture file must be a PNG: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _texture_ref(mod_id: str, kind: str, definition: ItemDef | BlockDef) -> str:
    if definition.texture:
        return normalize_ref(definition.texture, default_namespace=mod_id)
    return f"{mod_id}:{kind}/{definition.id}"


def _block_model_json(mod_id: str, definition: BlockDef) -> dict[str, Any]:
    if definition.textures:
        return {
            "parent": "minecraft:block/cube",
            "textures": {
                face: normalize_ref(texture, default_namespace=mod_id)
                for face, texture in definition.textures.items()
            },
        }
    if definition.texture_files:
        return {
            "parent": "minecraft:block/cube",
            "textures": {
                face: f"{mod_id}:block/{definition.id}/{face}"
                for face in definition.texture_files
            },
        }

    return {
        "parent": "minecraft:block/cube_all",
        "textures": {"all": _texture_ref(mod_id, "block", definition)},
    }


def _ingredient_json(ref: str, mod_id: str) -> dict[str, str]:
    if ref.startswith("#"):
        return {"tag": normalize_ref(ref[1:], default_namespace=mod_id)}
    return {"item": normalize_ref(ref, default_namespace=mod_id)}


def _result_json(ref: str, count: int, mod_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {"id": normalize_ref(ref, default_namespace=mod_id)}
    if count != 1:
        result["count"] = count
    return result


def _ensure_can_register_item(id: str) -> None:
    if any(definition.id == id for definition in _items):
        raise ValueError(f"duplicate item id: {id!r}")
    if any(definition.id == id and definition.needs_block_item for definition in _blocks):
        raise ValueError(f"item id conflicts with generated block item: {id!r}")


def _ensure_can_register_block(id: str, *, needs_block_item: bool) -> None:
    if any(definition.id == id for definition in _blocks):
        raise ValueError(f"duplicate block id: {id!r}")
    if needs_block_item and any(definition.id == id for definition in _items):
        raise ValueError(f"block item id conflicts with item: {id!r}")


def _ensure_recipe_id_available(id: str) -> None:
    if any(definition.id == id for definition in _shaped_recipes):
        raise ValueError(f"duplicate recipe id: {id!r}")
    if any(definition.id == id for definition in _shapeless_recipes):
        raise ValueError(f"duplicate recipe id: {id!r}")


def _ensure_one_texture_source(*, texture: str | None, texture_file: str | Path | None) -> None:
    if texture is not None and texture_file is not None:
        raise ValueError("use either texture or texture_file, not both")


def _ensure_one_block_texture_source(
    *,
    texture: str | None,
    texture_file: str | Path | None,
    textures: dict[str, str] | None,
    texture_files: dict[str, str | Path] | None,
) -> None:
    provided = [
        texture is not None,
        texture_file is not None,
        textures is not None,
        texture_files is not None,
    ]
    if sum(provided) > 1:
        raise ValueError("use only one of texture, texture_file, textures, or texture_files")


def _normalize_face_texture_refs(textures: dict[str, str]) -> dict[str, str]:
    _validate_face_texture_keys(textures)
    return {
        _normalize_face(face): normalize_ref(texture)
        for face, texture in textures.items()
    }


def _normalize_face_texture_files(texture_files: dict[str, str | Path]) -> dict[str, str]:
    _validate_face_texture_keys(texture_files)
    return {
        _normalize_face(face): str(path)
        for face, path in texture_files.items()
    }


def _validate_face_texture_keys(textures: dict[str, object]) -> None:
    normalized_faces = {_normalize_face(face) for face in textures}
    expected = {"north", "south", "east", "west", "up", "down"}
    missing = expected - normalized_faces
    extra = normalized_faces - expected
    if missing or extra:
        raise ValueError(
            "face textures must define exactly north, south, east, west, up, and down"
        )


def _normalize_face(face: str) -> str:
    aliases = {
        "top": "up",
        "bottom": "down",
    }
    normalized = aliases.get(face, face)
    if normalized not in {"north", "south", "east", "west", "up", "down"}:
        raise ValueError(f"invalid block face: {face!r}")
    return normalized


def _validate_count(count: int) -> None:
    if count < 1:
        raise ValueError("count must be 1 or greater")


def _validate_stack_size(max_stack_size: int) -> None:
    if max_stack_size < 1 or max_stack_size > 99:
        raise ValueError("max_stack_size must be between 1 and 99")


def _validate_pattern(pattern: list[str], key: dict[str, str]) -> None:
    if not pattern:
        raise ValueError("shaped recipe pattern cannot be empty")
    width = len(pattern[0])
    if width == 0 or width > 3 or len(pattern) > 3:
        raise ValueError("shaped recipe pattern must fit within a 3x3 crafting grid")
    if any(len(row) != width for row in pattern):
        raise ValueError("all shaped recipe pattern rows must have the same width")

    used_symbols = {symbol for row in pattern for symbol in row if symbol != " "}
    if len(used_symbols) != len(key) or used_symbols != set(key):
        raise ValueError("shaped recipe key must exactly match non-space pattern symbols")
    for symbol in key:
        if len(symbol) != 1 or symbol == " ":
            raise ValueError("shaped recipe key symbols must be one non-space character")


def _validate_id(id: str) -> None:
    if not id:
        raise ValueError("id cannot be empty")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    if any(char not in allowed for char in id):
        raise ValueError(f"id must use lowercase letters, numbers, and underscores only: {id!r}")


def normalize_ref(ref: str, default_namespace: str | None = None) -> str:
    raw = ref.strip()
    if not raw:
        raise ValueError("resource reference cannot be empty")
    if ":" in raw:
        namespace, path = raw.split(":", 1)
        _validate_namespace(namespace)
        _validate_resource_path(path)
        return raw
    if default_namespace is None:
        return raw
    _validate_resource_path(raw)
    return f"{default_namespace}:{raw}"


def _validate_namespace(namespace: str) -> None:
    if not namespace:
        raise ValueError("resource namespace cannot be empty")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_.-")
    if any(char not in allowed for char in namespace):
        raise ValueError(f"invalid resource namespace: {namespace!r}")


def _validate_resource_path(path: str) -> None:
    if not path:
        raise ValueError("resource path cannot be empty")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_./-")
    if any(char not in allowed for char in path):
        raise ValueError(f"invalid resource path: {path!r}")


def normalize_minecraft_version(version: int | str) -> str:
    raw = str(version).strip()
    if not raw:
        raise ValueError("mod_version cannot be empty")

    if "." in raw:
        parts = raw.split(".")
        if len(parts) not in (2, 3) or any(not part.isdigit() for part in parts):
            raise ValueError(f"invalid Minecraft version: {version!r}")
        return raw

    if not raw.isdigit():
        raise ValueError(f"invalid mod_version code: {version!r}")

    if len(raw) in (4, 5):
        return f"{int(raw[0])}.{int(raw[1:3])}.{int(raw[3:])}"
    if len(raw) == 3:
        return f"{int(raw[0])}.{int(raw[1:])}"

    raise ValueError("mod_version must look like 1211, 12110, 119, or 1.21.1")
