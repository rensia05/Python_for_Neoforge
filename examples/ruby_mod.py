from pyneoforge import block, config, creative_tab, item, shaped_recipe, shapeless_recipe

config(mod_version=1211)
item("ruby", display_name="Ruby", texture="python_for_neoforge:item/ruby")
block(
    "ruby_block",
    display_name="Ruby Block",
    hardness=5.0,
    resistance=6.0,
    max_stack_size=64,
    texture="python_for_neoforge:block/ruby_block",
)
block(
    "ruby_machine",
    display_name="Ruby Machine",
    hardness=4.0,
    resistance=6.0,
    textures={
        "north": "python_for_neoforge:block/ruby_machine/front",
        "south": "python_for_neoforge:block/ruby_machine/side",
        "east": "python_for_neoforge:block/ruby_machine/side",
        "west": "python_for_neoforge:block/ruby_machine/side",
        "up": "python_for_neoforge:block/ruby_machine/top",
        "down": "python_for_neoforge:block/ruby_machine/bottom",
    },
)

creative_tab(
    "main",
    display_name="Python for NeoForge",
    icon="ruby",
    entries=["ruby", "ruby_block", "ruby_machine"],
)

shaped_recipe(
    "ruby_block",
    result="ruby_block",
    pattern=["RRR", "RRR", "RRR"],
    key={"R": "ruby"},
)

shapeless_recipe(
    "ruby_from_block",
    result="ruby",
    ingredients=["ruby_block"],
    count=9,
)
