#!/usr/bin/python3
""" 
Generate recipe advancements, based on command-line args.
Intended for use in scripts to generate recipe advancement JSON files.

Must be run in src/main/resources/data/<modid>/advancements/recipes.

SYNOPSIS:

make_recipe_advancements.py [-h] [-i ITEM]
                                   recipe_list [recipe_list ...]

Generate recipe advancements

positional arguments:
  recipe_list           list of recipes to be granted

optional arguments:
  -h, --help            show this help message and exit
  -i ITEM, --item ITEM  id of item whose possession triggers the advancement

"""

import sys
import os
import os.path
import argparse
import json
import copy

ADVANCEMENT_TEMPLATE = {
    "parent" : None,
    "rewards": {
        "recipes": [
        ]
    },
    "criteria" : {
        "has_item" : {
            "trigger": "minecraft:inventory_changed",
            "conditions" : {
                "items" : [
                    { "item" : None}
                ]
           }
        }
    },
    "requirements": [
        [ "has_item" ]
    ]
}

# command-line arguments
parser = argparse.ArgumentParser(description="Generate recipe advancements")
parser.add_argument("recipe_list", help="list of recipes to be granted", 
    nargs='+')
parser.add_argument("-i","--item", help="id of item whose possession triggers the advancement")
args = parser.parse_args()
#print(args)

# parse directory and make sure we are in the right place...
# ...src/main/resources/data/<modid>/advancements/recipes.
(head, tail) = os.path.split(os.getcwd())
# head = ...src/main/resources/data/<modid>/advancements
(head2, tail2) = os.path.split(head)
if tail != 'recipes' or tail2 != 'advancements':
    print('Warning: not in advancements/recipes directory')
    exit()

# head2 = ...src/main/resources/data/<modid>
(head3, modid) = os.path.split(head2)
# head3 = ...src/main/resources/data
if not head3.endswith('data'):
    print('Warning: not in data/{}/advancements/recipes directory'.format(modid))
    exit()

shortname = args.item.split(':')[1]
filename = "{}.json".format(shortname)

recipe = copy.deepcopy(ADVANCEMENT_TEMPLATE)
recipe["parent"] = "{}:recipes/root".format(modid)
recipe["criteria"]["has_item"]["conditions"]["items"][0]["item"] = args.item
recipe["rewards"]["recipes"] = args.recipe_list

with open(filename, 'w') as f:
    json.dump(recipe, f, indent=4, sort_keys=False)

print("Recipe done")

