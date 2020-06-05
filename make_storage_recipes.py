#!/usr/bin/python3
"""
Generate standard item (default: ingot), block, and smaller item 
(default: nugget) storage recipe files.

Must be run in src/main/resources/data/<modid>/recipes.

SYNOPSIS:
usage: make_storage_recipes.py [-h] [-n] [-c] [-L] [-i ITEM] [-b BLOCK]
                               material

Generate standard storage block, ingot, and nugget recipes

positional arguments:
  material              material name for storage items and blocks; e.g 'iron'
                        for 'iron_block', 'iron_ingot', 'iron_nugget', etc

optional arguments:
  -h, --help            show this help message and exit
  -n, --no-nugget       do not generate nugget recipes
  -c, --conditions      insert flag condition into recipe. Will need editing.
  -L, --large-chunk     create recipe for large chunk
  -i ITEM, --item ITEM  alternate name for item
  -b BLOCK, --block BLOCK
                        alternate name for block

"""

import sys
import os
import os.path
import argparse
import json
import copy

STORAGE = ('block', 'ingot', 'ingot_from_nuggets', 'nugget', 'large_chunk',
           'nuggets_from_chunk')

PATTERN_TEMPLATES = { 
    'block' : ["SSS", "SSS", "SSS"],
    'ingot' : "shapeless" ,
    'ingot_from_nuggets' : ["###", "###", "###"],
    'nugget' : "shapeless",
    'large_chunk' : ["###","# #", "###"],
    'nuggets_from_chunk' : "shapeless"
}

SHAPED_TEMPLATE = { 
    "type" : "minecraft:crafting_shaped",
    "conditions" : [], 
    "pattern" : None,
    "key" : {  },
    "result" : { "item" : None }
}

SHAPELESS_TEMPLATE = { 
    "type" : "minecraft:crafting_shapeless",
    "conditions" : [], 
    "ingredients" : [ {"item" : None } ],
    "result" : { "item" : None, "count" : 9 } 
}

INGREDIENT_TEMPLATE = { 
    "item" : None,
    "count" : 1
}

CONDITION_TEMPLATE = { "type" : None, "flag" : None }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate standard storage block, ingot, and nugget recipes")
parser.add_argument("material", help="material name for storage items and blocks; e.g 'iron' for 'iron_block', 'iron_ingot', 'iron_nugget', etc")
parser.add_argument("-n","--no-nugget", action="store_true",
        help="do not generate nugget recipes", default=False)
parser.add_argument("-c", "--conditions", action="store_true",
        help="insert flag condition into recipe. Will need editing.")
parser.add_argument("-L", "--large-chunk", action="store_true",
        help="create recipe for large chunk")
parser.add_argument("-i","--item", help="alternate name for item",
        default="ingot")
parser.add_argument("-b","--block", help="alternate name for block",
        default="block")

args = parser.parse_args()
#print(args);

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

mod_storage = list(STORAGE)
mod_storage[0] = args.block
mod_storage[1] = args.item
mod_storage[2] = "{}_from_nuggets".format(args.item)
for ii,v in enumerate(STORAGE):
    if STORAGE[ii] != mod_storage[ii]:
        PATTERN_TEMPLATES[mod_storage[ii]] = PATTERN_TEMPLATES[STORAGE[ii]]

#print(PATTERN_TEMPLATES)

slist = ["{}_{}".format(args.material, a) for a in mod_storage] 
block_name = slist[0]
ingot_name = slist[1]
ingot2_name = slist[2]
nugget_name = slist[3]
slist[4] = "large_{}_chunk".format(args.material)
large_chunk_name = slist[4]

item_list = slist[0:2]
if not args.no_nugget:
    item_list.extend(slist[2:4])
if args.large_chunk:
    item_list.extend(slist[4:6])

ingredients = { a: None for a in mod_storage}
ingredients["block"] = ingot_name
ingredients["ingot"] = block_name
ingredients["ingot_from_nuggets"] = nugget_name
ingredients["nugget"] = ingot_name
ingredients["large_chunk"] = nugget_name
ingredients["nuggets_from_chunk"] = large_chunk_name

print("Generating {} recipes for mod {}:".format(args.material, modid))
for a in item_list:
    print("\t",a)
print()
ok = input("Is this okay? ")
if ok[0:1].lower() != 'y':
    exit()
print()
 
# get my constants:
pattern_dict = {"S" : "material_item", "#" : "nugget" }
pattern_dict["S"] = "{}:{}_{}".format(modid, args.material, args.item)
pattern_dict["#"] = "{}:{}_{}".format(modid, args.material, "nugget")


# cycle through items, select conditions, write file.
for item in item_list:
    filename = "{}.json".format(item)
    print("Creating {} for item {}".format( filename, item))
    result_item = item
    if item.startswith('large'):
        type_of_item = 'large_chunk'
    elif item.endswith('nuggets'):
        type_of_item = 'ingot_from_nuggets'
        result_item = "{}_{}".format(args.material, args.item)
    elif item.endswith('nuggets_from_chunk'):
        type_of_item = 'nuggets_from_chunk'
        result_item = "{}_{}".format(args.material, 'nugget')
    else:
        type_of_item = item.rsplit("_",1)[1]
    print("type of item: ", type_of_item)

    # shapeless recipes
    if PATTERN_TEMPLATES[type_of_item] == 'shapeless':
        recipe = copy.deepcopy(SHAPELESS_TEMPLATE)
        recipe["ingredients"][0]["item"] = "{}:{}".format(modid, 
                                                    ingredients[type_of_item])
    # shaped recipes
    else:
        recipe = copy.deepcopy(SHAPED_TEMPLATE)
        recipe["pattern"] = PATTERN_TEMPLATES[type_of_item]
        if any('S' in a for a in recipe["pattern"]):
            recipe["key"]["S"] = {"item" : pattern_dict["S"] }
        if any('#' in a for a in recipe["pattern"]):
            recipe["key"]["#"] = {"item" : pattern_dict["#"] }
    # end-else

    recipe["result"]["item"] = "{}:{}".format(modid, result_item)
    if type_of_item == 'nuggets_from_chunk':
            recipe["result"]["count"] = 8

    if args.conditions:
        mycondition = copy.deepcopy(CONDITION_TEMPLATE)
        mycondition["type"] = "{}:flag".format(modid)
        mycondition["flag"] = "{}_tools_enabled".format(args.material);
        recipe["conditions"].append(mycondition)
    else:
        del recipe["conditions"]
        
    with open(filename, 'w') as f:
        json.dump(recipe, f, indent=4, sort_keys=True)

print("Recipes done")


