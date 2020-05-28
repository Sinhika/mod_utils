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
        --nostore - do not generate recipes for default storage items (block,
                    ingot, nugget, large chunk)
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
STORAGE = ('block', 'ingot', 'ingot_from_nuggets', 'nugget', 'large_chunk')

PATTERN_TEMPLATES = { 'axe' : [ "SS ", "ST ", " T " ], 
        'hoe' : [ "SS ", " T ", " T " ], 
        'pickaxe' : ["SSS", " T ", " T "],
        'shears' : ["S ", " S"], 
        'shovel' : [" S ", " T ", " T "],
        'sword' : [ " S ", " S ", " T "],
        'boots' : [ "S S", "S S"],
        'chestplate' : ["S S", "SSS", "SSS"],
        'helmet' : ["SSS", "S S"],
        'leggings' : ["SSS", "S S", "S S"],
        'block' : ["SSS", "SSS", "SSS"],
        'ingot' : "shapeless" ,
        'ingot_from_nuggets' : ["###", "###", "###"],
        'nugget' : "shapeless",
        'large_chunk' : ["###","# #", "###"]
        }

RECIPE_TEMPLATE = { "conditions" : [], 
        "result" : { "item" : None },
        "pattern" : None,
        "type" : "minecraft:crafting_shaped",
        "key" : {  }
    }

VANILLA_RECYCLING_TEMPLATE = { "type" : "minecraft:smelting",
        "ingredient" : [],
        "result" : None,
        "experience" : 0.2,
        "cookingtime" : 200
    }

INGREDIENT_TEMPLATE = { "item" : None,
        "count" : 1
        }

INGOT_TEMPLATE = { "conditions" : [], 
        "type" : "minecraft:crafting_shapeless",
        "ingredients" : [ {"item" : None } ],
        "result" : { "item" : None, "count" : 9 } }

CONDITION_TEMPLATE = { "type" : None, "flag" : None }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate standard tool, armor and storage block recipes")
parser.add_argument("tooltype_prefix", help="tool material-based prefix for standard tools; e.g. 'iron' for 'iron_axe','iron_pickaxe', etc")
parser.add_argument("-a", "--armor", action="store_true",
        help="also generate armor recipes for material");
parser.add_argument("--nostore", action="store_true",
        help="do not generate recipes for default storage items (block, ingot, nugget)")
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
ingot_name = None
ingot2_name = None
block_name = None
nugget_name = None
large_chunk_name = None

item_list = ["{}_{}".format(args.tooltype_prefix, a) for a in TOOLS]
if args.armor:
    armor_list = ["{}_{}".format(args.tooltype_prefix, a) for a in ARMORS]
    item_list.extend(armor_list)
if not args.nostore:
    slist = ["{}_{}".format(args.tooltype_prefix, a) for a in STORAGE] 
    block_name = slist[0]
    ingot_name = slist[1]
    ingot2_name = slist[2]
    nugget_name = slist[3]
    slist[4] = "large_{}_chunk".format(args.tooltype_prefix)
    large_chunk_name = slist[4]
    item_list.extend(slist)
print("Generating {} recipes for mod {}:".format(args.tooltype_prefix, modid))
for a in item_list:
    print("\t",a)
print()
ok = input("Is this okay? ")
if ok[0:1].lower() != 'y':
    exit()
print()
 
# get my constants:
pattern_dict = {"S" : "metal element", "T" : "stick element", "#" : "nugget" }

pattern_dict["S"] = "{}:{}_{}".format(modid, args.tooltype_prefix, "ingot")
pattern_dict["T"] = "forge:rods/wooden"
pattern_dict["#"] = "{}:{}_{}".format(modid, args.tooltype_prefix, "nugget")

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

    if item.startswith('large'):
        type_of_item = 'large_chunk'
    elif item.endswith('nuggets'):
        type_of_item = 'ingot_from_nuggets'
    else:
        type_of_item = item.rsplit("_",1)[1]
    print("type of item: ", type_of_item)

    if (type_of_item not in STORAGE) or (item == block_name):
        recipe = copy.deepcopy(RECIPE_TEMPLATE)
        recipe["result"]['item'] = "{}:{}".format(modid, item)
        recipe["pattern"] = PATTERN_TEMPLATES[type_of_item]
        # build recipe key
        if any('S' in a for a in recipe["pattern"]):
            recipe["key"]["S"] = {"item" : pattern_dict["S"] }
        if any('T' in a for a in recipe["pattern"]):
            recipe["key"]["T"] = {"tag" : pattern_dict["T"] }
    elif item in (ingot2_name, large_chunk_name):
        recipe = copy.deepcopy(RECIPE_TEMPLATE)
        if item == ingot2_name:
            recipe["result"]['item'] = "{}:{}".format(modid, ingot_name)
            recipe["pattern"] = PATTERN_TEMPLATES['ingot_from_nuggets']
        else:
            recipe["result"]['item'] = "{}:{}".format(modid, large_chunk_name)
            recipe["pattern"] = PATTERN_TEMPLATES['large_chunk']
        # build recipe key
        recipe["key"]["#"] = {"item" : pattern_dict["#"] }
    else:
        recipe = copy.deepcopy(INGOT_TEMPLATE)
        if item == ingot_name:
            recipe["result"]['item'] = "{}:{}".format(modid, ingot_name)
            recipe["ingredients"][0]["item"] = "{}:{}".format(modid, block_name) 
        elif item == nugget_name:
            recipe["result"]['item'] = "{}:{}".format(modid, nugget_name)
            recipe["ingredients"][0]["item"] = "{}:{}".format(modid, ingot_name) 

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

