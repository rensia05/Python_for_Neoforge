# Python_for_Neoforge

Write basic NeoForge mods in Python, then package them into a normal `.jar` mod.

## User Workflow

Install the Python tool:

```powershell
pip install pyneoforge
```

Create a new mod project:

```powershell
pyneoforge init ruby_mod --mod-id ruby_mod --mod-name "Ruby Mod"
cd ruby_mod
```

Edit `mod.py`:

```python
from pyneoforge import block, config, creative_tab, item, shaped_recipe

config(mod_version=1211)

item("ruby", display_name="Ruby", texture_file="textures/ruby.png")
block("ruby_block", display_name="Ruby Block", hardness=5.0, max_stack_size=64, texture_file="textures/ruby_block.png")

creative_tab("main", display_name="Ruby Mod", icon="ruby", entries=["ruby", "ruby_block"])

shaped_recipe(
    "ruby_block",
    result="ruby_block",
    pattern=["RRR", "RRR", "RRR"],
    key={"R": "ruby"},
)
```

Put PNG textures beside the script:

```text
ruby_mod/
  mod.py
  textures/
    ruby.png
    ruby_block.png
```

Build a NeoForge jar:

```powershell
pyneoforge package
```

The finished jar is written to:

```text
dist/ruby_mod-0.1.0.jar
```

Put that jar in a NeoForge `mods` folder.

## Block Textures

Simple blocks need one texture:

```python
block("ruby_block", texture_file="textures/ruby_block.png")
```

Blocks can also use different textures per face:

```python
block(
    "ruby_machine",
    textures={
        "north": "ruby_mod:block/ruby_machine/front",
        "south": "ruby_mod:block/ruby_machine/side",
        "east": "ruby_mod:block/ruby_machine/side",
        "west": "ruby_mod:block/ruby_machine/side",
        "up": "ruby_mod:block/ruby_machine/top",
        "down": "ruby_mod:block/ruby_machine/bottom",
    },
)
```

Or copy six PNG files directly:

```python
block(
    "ruby_machine",
    texture_files={
        "north": "textures/ruby_machine_front.png",
        "south": "textures/ruby_machine_side.png",
        "east": "textures/ruby_machine_side.png",
        "west": "textures/ruby_machine_side.png",
        "up": "textures/ruby_machine_top.png",
        "down": "textures/ruby_machine_bottom.png",
    },
)
```

`top` and `bottom` are accepted as aliases for `up` and `down`.

## Requirements

- Python 3.10+
- Java 21 for Minecraft/NeoForge 1.21.1
- Gradle on `PATH`

By default, generated Gradle projects use:

```properties
org.gradle.java.home=C:/Program Files/Java/jdk-21
neo_version=21.1.200
```

You can override them:

```powershell
pyneoforge package mod.py --mod-id ruby_mod --mod-name "Ruby Mod" --java-home "C:/Java/jdk-21" --neo-version 21.1.200
```

## Developer Workflow

Install this repository in editable mode:

```powershell
pip install -e .
```

Generate resources into the checked-in NeoForge project:

```powershell
python -m pyneoforge.build examples/ruby_mod.py --mod-id python_for_neoforge --mod-version 1211
```

Build the development mod:

```powershell
cd neoforge-mod
.\gradlew.bat build
```
