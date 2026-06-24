# Python_for_Neoforge

[[README_KR.md]] - Korean Readme

Fully Workable and Compatiable with 1.21.1 NeoForge Version!

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

Or create a project from an existing script:

```powershell
pyneoforge init ruby_mod --from path/to/my_mod.py --mod-id ruby_mod --mod-name "Ruby Mod"
cd ruby_mod
```

If `path/to/textures/` exists beside `my_mod.py`, it is copied into the new project.

Edit `mod.py`:

```python
from pyneoforge import block, config, creative_tab, custom_tier, food, item, pickaxe, shaped_recipe, sword

config(mod_version=1211)

item("example_item", display_name="Example Item", texture_file="textures/example_item.png")
custom_tier(
    "example",
    durability=900,
    mining_speed=7.0,
    attack_damage_bonus=2.5,
    enchantment_value=18,
    repair_ingredient="example_item",
    base_tier="diamond",
)
food("example_food", display_name="Example Food", nutrition=4, saturation=0.3, texture_file="textures/example_food.png")
sword("example_sword", display_name="Example Sword", tier="example", attack_damage=3.0, attack_speed=-2.4, texture_file="textures/example_sword.png")
pickaxe("example_pickaxe", display_name="Example Pickaxe", tier="example", texture_file="textures/example_pickaxe.png")
block("example_block", display_name="Example Block", hardness=5.0, max_stack_size=64, texture_file="textures/example_block.png")

creative_tab("main", display_name="Ruby Mod", icon="example_item", entries=["example_item", "example_food", "example_sword", "example_pickaxe", "example_block"])

shaped_recipe(
    "example_block",
    result="example_block",
    pattern=["RRR", "RRR", "RRR"],
    key={"R": "example_item"},
)
```

Put PNG textures beside the script:

```text
ruby_mod/
  mod.py
  textures/
    example_item.png
    example_food.png
    example_sword.png
    example_pickaxe.png
    example_block.png
```

Build a NeoForge jar:

```powershell
pyneoforge package
```

If Windows cannot find the `pyneoforge` command, use the module form:

```powershell
python -m pyneoforge package
```

The finished jar is written to:

```text
dist/ruby_mod-0.1.0.jar
```

Put that jar in a NeoForge `mods` folder.

## Block Textures

## Food, Weapons, And Tools

Food items:

```python
food("apple_pie", display_name="Apple Pie", nutrition=6, saturation=0.8, always_edible=False, fast=False)
```

Weapons:

```python
sword("ruby_sword", display_name="Ruby Sword", tier="diamond", attack_damage=4.0, attack_speed=-2.4)
```

Tools:

```python
pickaxe("ruby_pickaxe", display_name="Ruby Pickaxe", tier="diamond")
```

Supported tool functions are `sword`, `pickaxe`, `axe`, `shovel`, and `hoe`.
Supported tiers are `wood`, `stone`, `iron`, `diamond`, `gold`, and `netherite`.

Custom tiers let you define durability and repair material:

```python
custom_tier(
    "ruby",
    durability=900,
    mining_speed=7.0,
    attack_damage_bonus=2.5,
    enchantment_value=18,
    repair_ingredient="ruby",
    base_tier="diamond",
)

sword("ruby_sword", tier="ruby")
pickaxe("ruby_pickaxe", tier="ruby")
```

`base_tier` controls vanilla mining restrictions. For example, `base_tier="diamond"` makes the custom tier behave like diamond for which blocks it can harvest.

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
