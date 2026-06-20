from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from importlib import resources
import os
from pathlib import Path
import runpy
import shutil
import subprocess

from .registry import build, clear


DEFAULT_MOD_ID = "python_for_neoforge"
DEFAULT_NEO_VERSION = "21.1.200"
DEFAULT_JAVA_HOME = "C:/Program Files/Java/jdk-21"
PLACEHOLDER_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAKUlEQVR4nGNkYGD4z0ABYBw1gGE0"
    "DBqGgYGBgYGBgYGBgQEAOwsCH2f3uAkAAAAASUVORK5CYII="
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyneoforge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a new Python NeoForge mod project.")
    init_parser.add_argument("path", help="Directory to create")
    init_parser.add_argument("--mod-id", default="my_python_mod")
    init_parser.add_argument("--mod-name", default="My Python Mod")

    build_parser = subparsers.add_parser("build", help="Generate NeoForge resources from a Python script.")
    build_parser.add_argument("script", help="Python mod definition script")
    build_parser.add_argument("--mod-id", default=DEFAULT_MOD_ID)
    build_parser.add_argument("--mod-version", help="Minecraft target version code, for example 1211 -> 1.21.1")
    build_parser.add_argument("--resources", default="neoforge-mod/src/main/resources")

    package_parser = subparsers.add_parser("package", help="Build a distributable NeoForge jar from a Python script.")
    package_parser.add_argument("script", nargs="?", default="mod.py", help="Python mod definition script")
    package_parser.add_argument("--mod-id")
    package_parser.add_argument("--mod-name")
    package_parser.add_argument("--mod-version", help="Your mod's version, not the Minecraft version")
    package_parser.add_argument("--mc-version", "--minecraft-version", dest="minecraft_version")
    package_parser.add_argument("--neo-version", default=DEFAULT_NEO_VERSION)
    package_parser.add_argument("--java-home")
    package_parser.add_argument("--output", default="dist")
    package_parser.add_argument("--work-dir", default=".pyneoforge/build")
    package_parser.add_argument("--keep-work-dir", action="store_true")

    args = parser.parse_args()
    if args.command == "init":
        init_project(args)
    elif args.command == "build":
        build_resources(args)
    elif args.command == "package":
        package_mod(args)


def init_project(args: argparse.Namespace) -> None:
    project_dir = Path(args.path)
    project_dir.mkdir(parents=True, exist_ok=False)
    textures_dir = project_dir / "textures"
    textures_dir.mkdir()
    _write_placeholder_png(textures_dir / "example_item.png")
    _write_placeholder_png(textures_dir / "example_block.png")
    (project_dir / "mod.py").write_text(
        _example_mod_py(mod_id=args.mod_id, mod_name=args.mod_name),
        encoding="utf-8",
    )
    (project_dir / "pyneoforge.toml").write_text(
        "\n".join(
            [
                f'mod_id = "{args.mod_id}"',
                f'mod_name = "{args.mod_name}"',
                'minecraft_version = "1211"',
                'mod_version = "0.1.0"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Created {project_dir}")


def build_resources(args: argparse.Namespace) -> None:
    output = _generate_resources(
        script=Path(args.script),
        resources_dir=Path(args.resources),
        mod_id=args.mod_id,
        minecraft_version=args.mod_version,
    )
    print(f"Generated {output}")


def package_mod(args: argparse.Namespace) -> None:
    script = Path(args.script).resolve()
    config = _read_project_config(script.parent / "pyneoforge.toml")
    mod_id = args.mod_id or config.get("mod_id")
    mod_name = args.mod_name or config.get("mod_name")
    mod_version = args.mod_version or config.get("mod_version", "0.1.0")
    minecraft_version = args.minecraft_version or config.get("minecraft_version", "1211")
    java_home = args.java_home or config.get("java_home", DEFAULT_JAVA_HOME if os.name == "nt" else "")

    if not mod_id:
        raise SystemExit("missing --mod-id or pyneoforge.toml mod_id")
    if not mod_name:
        raise SystemExit("missing --mod-name or pyneoforge.toml mod_name")

    work_root = Path(args.work_dir).resolve()
    project_dir = work_root / mod_id
    output_dir = Path(args.output).resolve()

    if project_dir.exists():
        shutil.rmtree(project_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    _copy_template(project_dir)
    _apply_template_values(
        project_dir=project_dir,
        mod_id=mod_id,
        mod_name=mod_name,
        mod_version=mod_version,
        neo_version=args.neo_version,
        java_home=java_home,
    )

    _generate_resources(
        script=script,
        resources_dir=project_dir / "src" / "main" / "resources",
        mod_id=mod_id,
        minecraft_version=minecraft_version,
    )

    _run_gradle_build(project_dir)
    jar_path = _find_built_jar(project_dir)
    output_path = output_dir / jar_path.name
    shutil.copyfile(jar_path, output_path)

    if not args.keep_work_dir:
        shutil.rmtree(project_dir)

    print(f"Built {output_path}")


def _copy_template(destination: Path) -> None:
    template = resources.files("pyneoforge").joinpath("templates", "neoforge-mod")
    with resources.as_file(template) as template_path:
        shutil.copytree(template_path, destination)
    gradlew = destination / "gradlew"
    if gradlew.exists():
        gradlew.chmod(0o755)


def _apply_template_values(
    *,
    project_dir: Path,
    mod_id: str,
    mod_name: str,
    mod_version: str,
    neo_version: str,
    java_home: str,
) -> None:
    java_home_line = ""
    if java_home:
        normalized_java_home = java_home.replace("\\", "/")
        java_home_line = f"org.gradle.java.home={normalized_java_home}"

    replacements = {
        "__MOD_ID__": mod_id,
        "__MOD_NAME__": mod_name,
        "__MOD_VERSION__": mod_version,
        "__NEO_VERSION__": neo_version,
        "__JAVA_HOME_LINE__": java_home_line,
    }

    for path in project_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".jar", ".png"}:
            continue
        text = path.read_text(encoding="utf-8")
        for key, value in replacements.items():
            text = text.replace(key, value)
        path.write_text(text, encoding="utf-8")


def _generate_resources(*, script: Path, resources_dir: Path, mod_id: str, minecraft_version: str | None) -> Path:
    clear()
    with _pushd(script.parent):
        runpy.run_path(str(script), run_name="__main__")
        return build(mod_id=mod_id, resources_dir=resources_dir, mod_version=minecraft_version)


def _run_gradle_build(project_dir: Path) -> None:
    gradlew = project_dir / ("gradlew.bat" if os.name == "nt" else "gradlew")
    command = [str(gradlew if gradlew.exists() else "gradle"), "build"]
    subprocess.run(command, cwd=project_dir, check=True)


def _find_built_jar(project_dir: Path) -> Path:
    jars = sorted((project_dir / "build" / "libs").glob("*.jar"))
    if not jars:
        raise FileNotFoundError("Gradle build did not produce a jar")
    return jars[0]


def _read_project_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _write_placeholder_png(path: Path) -> None:
    path.write_bytes(base64.b64decode(PLACEHOLDER_PNG))


@contextmanager
def _pushd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _example_mod_py(*, mod_id: str, mod_name: str) -> str:
    return f'''from pyneoforge import block, config, creative_tab, item, shaped_recipe

config(mod_version=1211)

item("example_item", display_name="Example Item", texture_file="textures/example_item.png")
block("example_block", display_name="Example Block", hardness=5.0, texture_file="textures/example_block.png")

creative_tab("main", display_name="{mod_name}", icon="example_item", entries=["example_item", "example_block"])

shaped_recipe(
    "example_block",
    result="example_block",
    pattern=["RRR", "RRR", "RRR"],
    key={{"R": "example_item"}},
)
'''


if __name__ == "__main__":
    main()
