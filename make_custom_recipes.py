#!/usr/bin/python3
""" 

Generate a recipe, based on command-line args for all the details.
Intended for use in scripts to generate recipe JSON files.

Must be run in src/main/resources/data/<modid>/recipes.

SYNOPSIS:

make_custom_recipes.py -h 
make_custom_recipes.py -t {shaped,shapeless,smelting,smoking,blasting,campfire}
                        [-c] (-i INGREDIENT | -p PATTERN)
                             (-n COUNT | -k KEYS) [--xp XP] result result_count

Generate custom recipes

positional arguments:
  result                id of recipe result; e.g. 'foo:bar_tool'
  result_count          number of result items

optional arguments:
  -h, --help            show this help message and exit
  -t, --type {shaped,shapeless,smelting,smoking,blasting,campfire}
                        type of recipe
  -c, --conditions      insert flag condition into recipe. Will need editing.
  -i INGREDIENT, --ingredient INGREDIENT
                        id of shapeless or smelting/cooking ingredient
  -p PATTERN, --pattern PATTERN
                        shaped crafting pattern, e.g. '"SSS"," T "," T "'
  -n COUNT, --count COUNT
                        count of shapeless ingredients
  -k KEYS, --keys KEYS  key values for pattern, semi-colon separated; e.g.
                        'S=minecraft:iron;T=forge:items/wooden_rod'
  --xp XP               smelting xp

"""

import sys
import os
import os.path
import argparse
import json
import copy

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
    "result" : { "item" : None } 
}

# also used for blasting, smoking and campfire_cooking.
SMELTING_TEMPLATE = {
    "type" : "minecraft:smelting",
    "conditions" : [], 
    "ingredient" : { "item" : None },
    "result" : None,
    "experience" : 0.0,
    "cookingtime": 200
}

CONDITION_TEMPLATE = { "type" : None, "flag" : None }


# command-line arguments
parser = argparse.ArgumentParser(description="Generate custom recipes")
parser.add_argument("result", help="id of recipe result; e.g. 'foo:bar_tool'")
parser.add_argument("result_count", help="number of result items", type=int,
        default=1)
parser.add_argument("-t", "--type", choices=['shaped','shapeless','smelting',
                                         'smoking', 'blasting', 'campfire'],
                    help="type of recipe", required=True)
parser.add_argument("-c", "--conditions", action="store_true",
        help="insert flag condition into recipe. Will need editing.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-i","--ingredient", help="id of shapeless or smelting/cooking ingredient")
group.add_argument("-p","--pattern", help="shaped crafting pattern, e.g. '\"SSS\",\" T \",\" T \"'")
group2 = parser.add_mutually_exclusive_group()
group2.add_argument("-n","--count", type=int, default=1, help="count of shapeless ingredients")
group2.add_argument("-k","--keys", 
    help="key values for pattern, semi-colon separated; e.g. 'S=minecraft:iron;T=forge:items/wooden_rod'")
parser.add_argument("--xp", type=float, help="smelting xp")

args = parser.parse_args()
print(args, "\n")
# end command-line arguments

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

filename = "{}.json".format(args.result)

if args.type == 'shapeless':
    recipe = copy.deepcopy(SHAPELESS_TEMPLATE)
    recipe["ingredients"][0]["item"] = args.ingredient
    if args.count > 1:
        recipe["ingredients"][0]["count"] = args.count
    recipe["result"]["item"] = "{}:{}".format(modid, args.result)
    if args.result_count > 1:
        recipe["result"]["count"] = args.result_count
        
elif args.type == 'shaped':
    recipe = copy.deepcopy(SHAPED_TEMPLATE)
    recipe["result"]["item"] = "{}:{}".format(modid, args.result)
    if args.result_count > 1:
        recipe["result"]["count"] = args.result_count
    recipe["pattern"] = [a for a in args.pattern.split(',')]
    keylist = args.keys.split(';')
    for keystring in keylist:
        k,v = keystring.split('=')
        if "/" in v:
            recipe["key"][k] = { "tag" : v } 
        else:
            recipe["key"][k] = { "item" : v } 

elif (args.type == 'smelting') or (args.type == 'smoking') \
     or (args.type == 'blasting') or (args.type == 'campfire'):
    recipe = copy.deepcopy(SMELTING_TEMPLATE)
    filename = "{}_from_{}.json".format(args.result, args.type)
    recipe["ingredient"]["item"] = args.ingredient
    if "/" in args.ingredient:
        recipe["ingredients"]["tag"] = args.ingredient
        del recipe["ingredient"]["item"]
    recipe["result"] = "{}:{}".format(modid, args.result)
    recipe["experience"] = args.xp

    if args.type == 'smoking':
        recipe["type"] = "minecraft:smoking"
        recipe["cookingtime"] = 100

    elif args.type == 'blasting':
        recipe["type"] = "minecraft:blasting"
        recipe["cookingtime"] = 100

    elif args.type == 'campfire':
        recipe["type"] = "minecraft:campfire_cooking"
        recipe["cookingtime"] = 600

if args.conditions:
    mycondition = copy.deepcopy(CONDITION_TEMPLATE)
    mycondition["type"] = "{}:flag".format(modid)
    mycondition["flag"] = "{}_enabled".format(modid)
    recipe["conditions"].append(mycondition)
else:
    del recipe["conditions"]

with open(filename, 'w') as f:
    json.dump(recipe, f, indent=4, sort_keys=True)

print("Recipe done")

