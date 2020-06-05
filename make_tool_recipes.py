#!/usr/bin/python3
""" PYTHON EXERCISE IN READING/WRITING JSON FILES

Generate standard tool recipes, given material input. Outputs are
<prefix>_<toolname>.json recipe files.

Must be run in src/main/resources/data/<modid>/recipes.

SYNOPSIS:
    make_tool_recipes.py [--armor][--nostore] <tooltype_prefix>

    tooltype_prefix - tool material name to prefix 'axe', 'sword', etc.

    Options:
        --armor - also generate armor recipes for material
        --recycle_only - only do vanilla recycling recipes.

"""

import sys
import os
import os.path
import argparse
import json
import copy

TOOLS = ('axe', 'hoe', 'pickaxe', 'shears', 'shovel', 'sword')
ARMORS = ('boots', 'chestplate', 'helmet', 'leggings')

PATTERN_TEMPLATES = { 
    'axe' : [ "SS ", "ST ", " T " ], 
    'hoe' : [ "SS ", " T ", " T " ], 
    'pickaxe' : ["SSS", " T ", " T "],
    'shears' : ["S ", " S"], 
    'shovel' : [" S ", " T ", " T "],
    'sword' : [ " S ", " S ", " T "],
    'boots' : [ "S S", "S S"],
    'chestplate' : ["S S", "SSS", "SSS"],
    'helmet' : ["SSS", "S S"],
    'leggings' : ["SSS", "S S", "S S"]
}

RECIPE_TEMPLATE = { 
    "conditions" : [], 
    "result" : { "item" : None },
    "pattern" : None,
    "type" : "minecraft:crafting_shaped",
    "key" : {  }
}

VANILLA_RECYCLING_TEMPLATE = { 
    "type" : "minecraft:smelting",
    "ingredient" : [],
    "result" : None,
    "experience" : 0.2,
    "cookingtime" : 200
}

INGREDIENT_TEMPLATE = { 
    "item" : None,
    "count" : 1
}

CONDITION_TEMPLATE = { "type" : None, "flag" : None }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate standard tool, armor and storage block recipes")
parser.add_argument("tooltype_prefix", help="tool material-based prefix for standard tools; e.g. 'iron' for 'iron_axe','iron_pickaxe', etc")
parser.add_argument("-a", "--armor", action="store_true",
        help="also generate armor recipes for material");
parser.add_argument("-c", "--conditions", action="store_true",
        help="insert flag condition into recipe. Will need editing.")
parser.add_argument("--recycle_only", action="store_true",
        help="only generate vanilla recycling recipes")

args = parser.parse_args()

# parse directory and make sure we are in the right place...
(head, tail) = os.path.split(os.getcwd())
if tail != 'recipes':
    print('Warning: not in recipes directory')
    exit()
(head, modid) = os.path.split(head)
(head, tail) = os.path.split(head)
if tail != 'data':
    print('Warning: not in data/{}/recipes directory'.format(modid))
    exit()

# VANILLA RECYCLING RECIPES:
# smelting
filename = "{}_nugget_from_smelting.json".format(args.tooltype_prefix)
recyc_list = ["{}_{}".format(args.tooltype_prefix, a) for a in TOOLS]
if args.armor:
    armor_list = ["{}_{}".format(args.tooltype_prefix, a) for a in ARMORS]
    recyc_list.extend(armor_list)
recipe = copy.deepcopy(VANILLA_RECYCLING_TEMPLATE)
recipe["result"] = "{}:{}_nugget".format(modid, args.tooltype_prefix)
for item in recyc_list:
    ingredient = copy.deepcopy(INGREDIENT_TEMPLATE)
    ingredient["item"] = "{}:{}".format(modid, item)
    recipe["ingredient"].append(ingredient)
with open(filename, 'w') as f:
        json.dump(recipe, f, indent=4, sort_keys=True)

#blasting
filename = "{}_nugget_from_blasting.json".format(args.tooltype_prefix)
recipe["cookingtime"] = 100
recipe["type"] = "minecraft:blasting"
with open(filename, 'w') as f:
        json.dump(recipe, f, indent=4, sort_keys=True)

if (args.recycle_only):
    sys.exit(None)

# what all are we doing? Inform user.
item_list = ["{}_{}".format(args.tooltype_prefix, a) for a in TOOLS]
if args.armor:
    armor_list = ["{}_{}".format(args.tooltype_prefix, a) for a in ARMORS]
    item_list.extend(armor_list)
print("Generating {} recipes for mod {}:".format(args.tooltype_prefix, modid))
for a in item_list:
    print("\t",a)
print()
ok = input("Is this okay? ")
if ok[0:1].lower() != 'y':
    exit()
print()
 
# get my constants:
pattern_dict = {
    "S" : "{}:{}_{}".format(modid, args.tooltype_prefix, "ingot"), 
    "T" : "forge:rods/wooden" 
}

# tell the user what we settled on.
for c in pattern_dict.keys():
    print("{} will be {}".format(c, pattern_dict[c]))
ok = input("Is this okay? ")
if ok[0:1].lower() != 'y':
    exit()
print()

# cycle through items, select conditions, write file.
for item in item_list:
    filename = "{}.json".format(item)
    print("Creating {} for item {}".format( filename, item))

    type_of_item = item.rsplit("_",1)[1]
    print("type of item: ", type_of_item)

    recipe = copy.deepcopy(RECIPE_TEMPLATE)
    recipe["result"]['item'] = "{}:{}".format(modid, item)
    recipe["pattern"] = PATTERN_TEMPLATES[type_of_item]
    # build recipe key
    if any('S' in a for a in recipe["pattern"]):
        recipe["key"]["S"] = {"item" : pattern_dict["S"] }
    if any('T' in a for a in recipe["pattern"]):
        recipe["key"]["T"] = {"tag" : pattern_dict["T"] }

    if args.conditions:
        mycondition = copy.deepcopy(CONDITION_TEMPLATE)
        mycondition["type"] = "{}:flag".format(modid)
        mycondition["flag"] = "{}_tools_enabled".format(args.tooltype_prefix);
        recipe["conditions"].append(mycondition)
    else:
        del recipe["conditions"]

    with open(filename, 'w') as f:
        json.dump(recipe, f, indent=4, sort_keys=True)

print("Recipes done")

