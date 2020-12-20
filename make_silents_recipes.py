#!/usr/bin/python3
""" 

Generate a recipe, based on command-line args for all the details.
Intended for use in scripts to generate recipe JSON files.

Must be run in src/main/resources/data/<modid>/recipes.

SYNOPSIS:

usage: make_silents_recipes.py [-h] --type {crusher,alloy_smelter}
                               --ingredient INGREDIENT [INGREDIENT ...]
                               --result RESULT [RESULT ...]
                               filename

Generate Silents recipes

positional arguments:
  filename              specify base output filename

optional arguments:
  -h, --help            show this help message and exit
  --type {crusher,alloy_smelter}, -t {crusher,alloy_smelter}
                        type of recipe
  --ingredient INGREDIENT [INGREDIENT ...], -i INGREDIENT [INGREDIENT ...]
                        id of ingredient; optionally with count (alloy
                        smelter); e.g. 'foo:bar_dust,2' preface with # if a
                        tag
  --result RESULT [RESULT ...], -r RESULT [RESULT ...]
                        space-separated ids of recipe result; e.g.
                        'foo:bar_chunk'; optionally with secondary chance
                        (crusher) or count(alloy smelter); e.g
                        'foo:bar_dust,0.1'. preface tags with #

"""

import sys
import os
import os.path
import argparse
import json
import copy

CRUSHING_TEMPLATE = {
    "conditions" : [ { "modid" : "silents_mechanisms", 
                       "type" : "forge:mod_loaded"}],
    "type" : "silents_mechanisms:crushing",
    "process_time" : 300,
    "ingredient": None,
    "results" : []
}

ALLOY_TEMPLATE = {
    "conditions" : [ { "modid" : "silents_mechanisms", 
                       "type" : "forge:mod_loaded"}],
    "type" : "silents_mechanisms:alloy_smelting",
    "process_time" : 200,
    "ingredients" : [],
    "result": None
}

ITEM_TEMPLATE = { "item" : None }
ITEM_W_CHANCE_TMPL = { "item" : None, "chance" : 0.0 }
ITEM_W_COUNT_TMPL = { "item" : None, "count" : 1 }
TAG_TEMPLATE = { "tag" : None }
TAG_W_COUNT_TMPL = { "tag" : None, "count" : 1 }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate Silents recipes. Must be run in src/main/resources/data/<modid>/recipes")
parser.add_argument("filename", help="specify base output filename")
parser.add_argument("--type", "-t", choices=['crusher', 'alloy_smelter'],
                    help="type of recipe", required=True)
parser.add_argument("--ticks", "-k", type=int, help="process_time in ticks", default=300)
parser.add_argument("--ingredient", "-i", required=True, nargs='+',
        help="id of ingredient; optionally with count (alloy smelter); e.g. 'foo:bar_dust,2' preface with # if a tag")
parser.add_argument("--result","-r", required=True, nargs='+',
        help="space-separated ids of recipe result; e.g. 'foo:bar_chunk'; optionally with secondary chance (crusher) or count(alloy smelter); e.g 'foo:bar_dust,0.1'. preface tags with #")
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
if args.type == 'crusher':
    filename = "./crushing/{}.json".format(args.filename)
    if not os.path.exists("./crushing"):
        os.mkdir("./crushing")
else:
    filename = "./alloy_smelting/{}.json".format(args.filename)
    if not os.path.exists("./alloy_smelting"):
        os.mkdir("./alloy_smelting")

# build recipe
if args.type == 'crusher':
    recipe = copy.deepcopy(CRUSHING_TEMPLATE)
    recipe['process_time'] = args.ticks

    # parse ingredient list (only 1 is recognized)
    ingredient = args.ingredient[0]
    if ingredient.startswith('#'):
        recipe["ingredient"] = copy.deepcopy(TAG_TEMPLATE)
        recipe['ingredient']['tag'] = ingredient.lstrip('#')
    else:
        recipe['ingredient'] = copy.deepcopy(ITEM_TEMPLATE)
        recipe['ingredient']['item'] = ingredient

    # parse results list (all recognized)
    for rr in args.result:
        parts = rr.split(',')
        if len(parts) > 1:
            if '.' in parts[1]:
                result = copy.deepcopy(ITEM_W_CHANCE_TMPL)
                result['item'] = parts[0]
                result['chance'] = float(parts[1])
            else:
                result = copy.deepcopy(ITEM_W_COUNT_TMPL)
                result['item'] = parts[0]
                result['count'] = int(parts[1])

        else:
            result = copy.deepcopy(ITEM_TEMPLATE)
            result['item'] = parts[0]
        recipe['results'].append(result)

else:
    recipe = copy.deepcopy(ALLOY_TEMPLATE)
    recipe['process_time'] = args.ticks
   
    # ingredients
    for ii in args.ingredient:
        parts = ii.split(',')
        if len(parts) > 1 and parts[0].startswith('#'):
           ingredient =  copy.deepcopy(TAG_W_COUNT_TMPL)
           ingredient['tag'] = parts[0].lstrip('#')
           ingredient['count'] = int(parts[1])
        elif len(parts) > 1:
           ingredient =  copy.deepcopy(ITEM_W_COUNT_TMPL)
           ingredient['item'] = parts[0]
           ingredient['count'] = int(parts[1])
        elif parts[0].startswith('#'):
           ingredient =  copy.deepcopy(TAG_TEMPLATE)
           ingredient['tag'] = parts[0].lstrip('#')
        else:
           ingredient =  copy.deepcopy(ITEM_TEMPLATE)
           ingredient['item'] = parts[0]
        recipe['ingredients'].append(ingredient)
    
    # result
    parts = args.result[0].split(',')
    result = copy.deepcopy(ITEM_W_COUNT_TMPL)
    if len(parts) > 1:
        result['item'] = parts[0]
        result['count'] = int(parts[1])
    else:
        result['item'] = parts[0]
        result['count'] = 1;
    recipe['result'] = result
    
# write recipe
with open(filename, 'w') as f:
    json.dump(recipe, f, indent=4, sort_keys=False)

print("Recipe {} done".format(args.filename))

