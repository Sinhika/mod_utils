#!/usr/bin/python3
"""
Generate model jsons. Based on the old gen_model_jsons.pl script.

Must be run in src/main/resources/assets/<modid>/models

SYNOPSIS:

"""
import sys
import os
import os.path
import argparse
import json
import copy

# TEMPLATES
BLOCK_BLOCK = { "parent" : "block/cube_all", "textures" : { "all" : None }}
ITEM_BLOCK = { "parent" : None }

BLOCK_PLATE = {}
ITEM_PLATE = {}

# LOOKUP TABLES FOR types => templates
LOOKUP_BLOCK = { "block" : BLOCK_BLOCK }

LOOKUP_ITEM = { "blockitem" : ITEM_BLOCK }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate block & item models as specified")
parser.add_argument("modelname", help="model filename")
parser.add_argument("--item_only", "--item", help="item model only", action="store_true")
parser.add_argument("--type", "-t", 
        choices=['block', 'crop', 'facing', 'bars', 'doors', 'pane', 'stairs',
                 'pressure_plate', 'pillar', 'log', 'machine', 'blockitem', 'bow',
                 'armor_set', 'tool_set', 'inventory'], 
        help="type of blockstate", required=True)

args = parser.parse_args()
#print(args);

# parse directory and make sure we are in the right place...
(head, tail) = os.path.split(os.getcwd())
if tail != 'models':
    print('Warning: not in models directory')
    exit()
(head, modid) = os.path.split(head)
(head, tail) = os.path.split(head)
if tail != 'assets':
    print('Warning: not in assets/{}/models directory'.format(modid))
    exit()

BLOCK_MODEL_PATH = os.path.join(os.getcwd(), 'block')
ITEM_MODEL_PATH =  os.path.join(os.getcwd(), 'item')

# construct the models
# blocks
if not args.item_only:
    block_model = copy.deepcopy(LOOKUP_BLOCK[args.type])
    if args.type in ('block',):
        texture = "{}:block/{}".format(modid, args.modelname)
        block_model['textures']['all'] = texture
    # TODO
    
    filename = os.join(BLOCK_MODEL_PATH, "{}.json".format(args.modelname))
    with open(filename, 'w') as f:
        json.dump(block_model, f, indent=4, sort_keys=False)

# items
item_model = copy.deepcopy(LOOKUP_ITEM[args.type])
if args.type in ('block','blockitem'):
    item_model = copy.deepcopy(LOOKUP_ITEM[args.type])
    if args.type in ('block',):
        parent = "{}:block/{}".format(modid, args.modelname)
        item_model['parent'] = parent
    #TODO

filename = os.join(ITEM_MODEL_PATH, "{}.json".format(args.modelname))
with open(filename, 'w') as f:
    json.dump(item_model, f, indent=4, sort_keys=False)

