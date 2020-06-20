#!/usr/bin/python3
""" 

Generate a recipe, based on command-line args for all the details.
Intended for use in scripts to generate recipe JSON files.

Must be run in src/main/resources/data/<modid>/recipes.

SYNOPSIS:

make_custom_recipes.py -h 
usage: make_custom_recipes.py -t {shaped,shapeless,smelting,smoking,blasting,campfire,fusion}
                            [-c] [--xp XP] [-f FILENAME]
                            (-i INGREDIENT | -p PATTERN | --catalyst CATALYST)
                            [-n COUNT | -k KEYS | -a ALLOY_INPUTS]
                            result result_count

Generate custom recipes

positional arguments:
  result                id of recipe result; e.g. 'foo:bar_tool'
  result_count          number of result items

optional arguments:
  -h, --help            show this help message and exit
  -t, --type {shaped,shapeless,smelting,smoking,blasting,campfire,fusion}
                        type of recipe
  -c, --conditions      insert flag condition into recipe. Will need editing.
  --xp XP               smelting xp
  -f FILENAME, --filename FILENAME
                        specify filename instead of using default, which is
                        the result
  -i INGREDIENT, --ingredient INGREDIENT
                        id of shapeless or smelting/cooking ingredient
  -p PATTERN, --pattern PATTERN
                        shaped crafting pattern, e.g. '"SSS"," T "," T "'
  --catalyst CATALYST   catalyst for fusion alloying, e.g.
                        'minecraft:redstone_dust'
  -n COUNT, --count COUNT
                        count of shapeless ingredients
  -k KEYS, --keys KEYS  key values for pattern, semi-colon separated; e.g.
                        'S=minecraft:iron;T=forge:items/wooden_rod'
  -a ALLOY_INPUTS, --alloy_inputs ALLOY_INPUTS
                        the 2 inputs to fusion alloying, semi-colon separated:
                        e.g. 'minecraft:iron; minecraft:items/coals'

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

# used for fusion_furnace alloy recipes.
FUSION_TEMPLATE = {
    "type" : "fusion:alloying",
    "conditions" : [],
    "output" : { "item" : None },
    "inputs" : [ { "item" : None }, {"item" : None} ],
    "catalyst" : { "item" : None },
    "experience" : 0.0,
    "cookingtime" : 600
}

CONDITION_TEMPLATE = { "type" : None, "flag" : None }


# command-line arguments
parser = argparse.ArgumentParser(description="Generate custom recipes")
parser.add_argument("result", help="id of recipe result; e.g. 'foo:bar_tool'")
parser.add_argument("result_count", help="number of result items", type=int,
        default=1)
parser.add_argument("-t", "--type", choices=['shaped','shapeless','smelting',
                                         'smoking', 'blasting', 'campfire', 
                                         'fusion'],
                    help="type of recipe", required=True)
parser.add_argument("-c", "--conditions", action="store_true",
        help="insert flag condition into recipe. Will need editing.")
parser.add_argument("--xp", type=float, help="smelting xp")
parser.add_argument("-f","--filename", help="specify filename instead of using default, which is the result")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-i","--ingredient", help="id of shapeless or smelting/cooking ingredient")
group.add_argument("-p","--pattern", help="shaped crafting pattern, e.g. '\"SSS\",\" T \",\" T \"'")
group.add_argument("--catalyst", help="catalyst for fusion alloying, e.g. 'minecraft:redstone_dust'")
group2 = parser.add_mutually_exclusive_group()
group2.add_argument("-n","--count", type=int, default=1, help="count of shapeless ingredients")
group2.add_argument("-k","--keys", 
    help="key values for pattern, semi-colon separated; e.g. 'S=minecraft:iron;T=forge:items/wooden_rod'")
group2.add_argument("-a","--alloy_inputs", 
        help="the 2 inputs to fusion alloying, semi-colon separated: e.g. 'minecraft:iron; minecraft:items/coals'")
args = parser.parse_args()
#print(args, "\n")
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

# get filename
if args.filename != None:
    filename = "{}.json".format(args.filename)
else:
    # clean up any ':'
    tempstr = args.result.split(':')[-1]
    if (args.type == 'smelting') or (args.type == 'smoking') \
        or (args.type == 'blasting') or (args.type == 'campfire'):
        filename = "{}_from_{}.json".format(tempstr, args.type)
    elif args.type == 'fusion':
        filename = "./fusion_furnace/{}.json".format(tempstr)
    else:
        filename = "{}.json".format(tempstr)

# fix up result name
if ':' in args.result:
    result = args.result
else:
    result = "{}:{}".format(modid, args.result)
    
if args.type == 'shapeless':
    recipe = copy.deepcopy(SHAPELESS_TEMPLATE)
    recipe["ingredients"][0]["item"] = args.ingredient
    if args.count > 1:
        recipe["ingredients"][0]["count"] = args.count
    recipe["result"]["item"] = result
    if args.result_count > 1:
        recipe["result"]["count"] = args.result_count
        
elif args.type == 'shaped':
    recipe = copy.deepcopy(SHAPED_TEMPLATE)
    recipe["result"]["item"] = result
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
    recipe["ingredient"]["item"] = args.ingredient
    if "/" in args.ingredient:
        recipe["ingredients"]["tag"] = args.ingredient
        del recipe["ingredient"]["item"]
    recipe["result"] = result
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

elif args.type == 'fusion':
    if not os.path.exists("./fusion_furnace"):
        os.mkdir("./fusion_furnace")
    recipe = copy.deepcopy(FUSION_TEMPLATE)
    recipe["output"]["item"] = result
    if args.result_count > 1:
        recipe["output"]["count"] = args.result_count
    inputs_list = args.alloy_inputs.split(';')
    recipe["inputs"][0]["item"] = inputs_list[0]
    recipe["inputs"][1]["item"] = inputs_list[1]
    recipe["catalyst"]["item"] = args.catalyst
    recipe["experience"] = args.xp

if args.conditions:
    mycondition = copy.deepcopy(CONDITION_TEMPLATE)
    mycondition["type"] = "{}:flag".format(modid)
    mycondition["flag"] = "{}_enabled".format(modid)
    recipe["conditions"].append(mycondition)
else:
    del recipe["conditions"]

with open(filename, 'w') as f:
    json.dump(recipe, f, indent=4, sort_keys=False)

print("Recipe done")

