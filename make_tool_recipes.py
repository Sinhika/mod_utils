#!/usr/bin/python3
""" PYTHON EXERCISE IN READING/WRITING JSON FILES

Generate standard tool recipes, given material input. Reads _constants.json
and _factories.json files to suggest ingredients and conditions. Outputs are
<prefix>_<toolname>.json recipe files.

Must be run in src/main/resources/assets/<modid>/recipes.

SYNOPSIS:
    make_tool_recipes.py [--armor][--nostore] <tooltype_prefix>

    tooltype_prefix - tool material name to prefix 'axe', 'sword', etc.

    Options:
        --armor - also generate armor recipes for material
        --nostore - do not generate recipes for default storage items (block,
                    ingot)

"""

import sys
import os
import os.path
import argparse
import json
import copy

TOOLS = ('axe', 'hoe', 'pickaxe', 'shears', 'shovel', 'sword')
ARMORS = ('boots', 'chestplate', 'helmet', 'leggings')
STORAGE = ('block', 'ingot')

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
        'ingot' : "shapeless" }

RECIPE_TEMPLATE = { "conditions" : [], 
        "result" : { "item" : None },
        "pattern" : None,
        "type" : "forge:ore_shaped",
        "key" : {  }
    }

INGOT_TEMPLATE = { "conditions" : [], 
        "type" : "minecraft:crafting_shapeless",
        "ingredients" : [ {"item" : None } ],
        "result" : { "item" : None, "count" : 9 } }

CONDITION_TEMPLATE = { "type" : None, "value" : "true" }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate standard tool, armor and storage block recipes")
parser.add_argument("tooltype_prefix", help="tool material-based prefix for standard tools; e.g. 'iron' for 'iron_axe','iron_pickaxe', etc")
parser.add_argument("-a", "--armor", action="store_true",
        help="also generate armor recipes for material");
parser.add_argument("--nostore", action="store_true",
        help="do not generate recipes for default storage items (block, ingot)")
args = parser.parse_args()

# parse directory and make sure we are in the right place...
(head, tail) = os.path.split(os.getcwd())
if tail != 'recipes':
    print('Warning: not in recipes directory')
    exit()
(head, modid) = os.path.split(head)
(head, tail) = os.path.split(head)
if tail != 'assets':
    print('Warning: not in assets/{}/recipes directory'.format(modid))
    exit()

# what all are we doing? Inform user.
ingot_name = None
block_name = None
item_list = ["{}_{}".format(args.tooltype_prefix, a) for a in TOOLS]
if args.armor:
    armor_list = ["{}_{}".format(args.tooltype_prefix, a) for a in ARMORS]
    item_list.extend(armor_list)
if not args.nostore:
    slist = ["{}_{}".format(args.tooltype_prefix, a) for a in STORAGE] 
    block_name = slist[0]
    ingot_name = slist[1]
    item_list.extend(slist)
print("Generating {} recipes for mod {}:".format(args.tooltype_prefix, modid))
for a in item_list:
    print("\t",a)
print()
ok = input("Is this okay? ")
if ok[0:1].lower() != 'y':
    exit()
print()
 
# look for _constants.json and import it, get constants
constants = None
if os.path.exists('_constants.json'):
    with open('_constants.json', 'r') as f:
        json_constants = json.load(f)
    constants = []
    for a in json_constants:
        constants.append(a['name'])
else:
    print("Warning: no _constants.json file!")
#print('constants =', constants)

# look for _factories.json and import it, get conditions
conditions = None
if os.path.exists('_factories.json'):
    with open('_factories.json', 'r') as f:
        json_factories = json.load(f)
    conditions = list(json_factories['conditions'].keys())
else:
    print("Warning: no _factories.json file!")
#print('conditions =', conditions)

# get my constants:
pattern_dict = {"S" : "metal element", "T" : "stick element" }
if constants:
    for c in sorted(pattern_dict.keys()):
        print("Which constant should represent {} ({})?".format(c, pattern_dict[c]))
        for count, constant in enumerate(constants):
            print("\t{}. {}".format(count, constant));
        N = int(input("Number? "))
        pattern_dict[c] = "#" + constants[N]
        print()    
else:
    pattern_dict["S"] = "{}:{}_{}".format(modid, args.tooltype_prefix, "ingot")
    pattern_dict["T"] = "minecraft:stick_wood"

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
    if item != ingot_name:
        recipe = copy.deepcopy(RECIPE_TEMPLATE)
        recipe["result"]['item'] = "{}:{}".format(modid, item)
        recipe["pattern"] = PATTERN_TEMPLATES[type_of_item]
        # build recipe key
        if any('S' in a for a in recipe["pattern"]):
            recipe["key"]["S"] = {"item" : pattern_dict["S"] }
        if any('T' in a for a in recipe["pattern"]):
            recipe["key"]["T"] = {"item" : pattern_dict["T"] }
    else:
        recipe = copy.deepcopy(INGOT_TEMPLATE)
        recipe["result"]['item'] = "{}:{}".format(modid, ingot_name)
        recipe["ingredients"][0]["item"] = "{}:{}".format(modid, block_name) 

    if conditions:
        done = False
        while not done:
            print("Possible conditions that might apply:")
            for jj, cond in enumerate(sorted(conditions)):
                print("\t{}. {}".format(jj, cond));
            N = input("Number or return or 'done'? ")
            if not N.isdigit():
                done = True
                print()
            else:
                N = int(N)
                mycondition = copy.deepcopy(CONDITION_TEMPLATE)
                mycondition["type"] = sorted(conditions)[N]
                recipe["conditions"].append(mycondition)

    with open(filename, 'w') as f:
        json.dump(recipe, f, indent=4, sort_keys=True)
        
print("Recipes done")

