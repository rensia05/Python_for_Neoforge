import json
from pathlib import Path

from pyneoforge import block, build, clear, config, creative_tab, food, item, pickaxe, shaped_recipe, shapeless_recipe, sword
from pyneoforge.registry import normalize_minecraft_version


def test_normalizes_compact_minecraft_versions() -> None:
    assert normalize_minecraft_version(1211) == "1.21.1"
    assert normalize_minecraft_version(12110) == "1.21.10"
    assert normalize_minecraft_version(1201) == "1.20.1"
    assert normalize_minecraft_version(119) == "1.19"


def test_build_writes_generated_resources(tmp_path: Path) -> None:
    clear()
    config(mod_version=1211)
    item("ruby", display_name="Ruby")
    food("ruby_apple", display_name="Ruby Apple", nutrition=6, saturation=0.8)
    sword("ruby_sword", display_name="Ruby Sword", tier="diamond", attack_damage=4.0, attack_speed=-2.4)
    pickaxe("ruby_pickaxe", display_name="Ruby Pickaxe", tier="diamond")
    block("ruby_block", display_name="Ruby Block", max_stack_size=16)
    block(
        "ruby_machine",
        display_name="Ruby Machine",
        textures={
            "north": "python_for_neoforge:block/ruby_machine/front",
            "south": "python_for_neoforge:block/ruby_machine/side",
            "east": "python_for_neoforge:block/ruby_machine/side",
            "west": "python_for_neoforge:block/ruby_machine/side",
            "up": "python_for_neoforge:block/ruby_machine/top",
            "down": "python_for_neoforge:block/ruby_machine/bottom",
        },
    )
    creative_tab("main", display_name="Python for NeoForge", icon="ruby", entries=["ruby", "ruby_block"])
    shaped_recipe("ruby_block", result="ruby_block", pattern=["RRR", "RRR", "RRR"], key={"R": "ruby"})
    shapeless_recipe("ruby_from_block", result="ruby", ingredients=["ruby_block"], count=9)

    build(mod_id="python_for_neoforge", resources_dir=tmp_path)

    generated_path = tmp_path / "assets/python_for_neoforge/pyneoforge/generated.json"
    assert generated_path.exists()
    generated = json.loads(generated_path.read_text(encoding="utf-8"))
    assert generated["items"][1]["kind"] == "food"
    assert generated["items"][1]["food"]["nutrition"] == 6
    assert generated["items"][2]["kind"] == "sword"
    assert generated["items"][2]["tier"] == "diamond"
    assert generated["blocks"][0]["max_stack_size"] == 16
    assert (tmp_path / "assets/python_for_neoforge/lang/en_us.json").exists()
    assert (tmp_path / "assets/python_for_neoforge/models/item/ruby.json").exists()
    assert (tmp_path / "assets/python_for_neoforge/blockstates/ruby_block.json").exists()
    assert (tmp_path / "assets/python_for_neoforge/models/block/ruby_block.json").exists()
    machine_model = json.loads(
        (tmp_path / "assets/python_for_neoforge/models/block/ruby_machine.json").read_text(encoding="utf-8")
    )
    assert machine_model["parent"] == "minecraft:block/cube"
    assert machine_model["textures"]["north"] == "python_for_neoforge:block/ruby_machine/front"
    assert (tmp_path / "assets/python_for_neoforge/models/item/ruby_block.json").exists()
    assert (tmp_path / "data/python_for_neoforge/recipe/ruby_block.json").exists()
    assert (tmp_path / "data/python_for_neoforge/recipe/ruby_from_block.json").exists()
