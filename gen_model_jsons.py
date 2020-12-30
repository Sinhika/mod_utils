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

BLOCK_PLATE = { 
        "parent" : "minecraft:block/pressure_plate_up",
        "textures" : None
    }
BLOCK_PLATE_DOWN = {
        "parent" : "minecraft:block/pressure_plate_down",
        "textures" : None
        }

# LOOKUP TABLES FOR types => templates
LOOKUP_BLOCK = { 'block' : BLOCK_BLOCK  }

LOOKUP_ITEM = { 'block' : ITEM_BLOCK, 'pressure_plate' : ITEM_BLOCK }

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
if not os.path.exists(BLOCK_MODEL_PATH):
    os.makedirs(BLOCK_MODEL_PATH)

ITEM_MODEL_PATH =  os.path.join(os.getcwd(), 'item')
if not os.path.exists(ITEM_MODEL_PATH):
    os.makedirs(ITEM_MODEL_PATH)

# construct the models
# blocks
if not args.item_only:
    if args.type in ('block',):
        block_model = copy.deepcopy(LOOKUP_BLOCK[args.type])
        texture = "{}:block/{}".format(modid, args.modelname)
        block_model['textures']['all'] = texture
    elif args.type == 'pressure_plate':
        # there are two model files for pressure plates...
        block_model = copy.deepcopy(BLOCK_PLATE_DOWN)
        texture = "{}:block/{}".format(modid, args.modelname)
        block_model['textures'] = texture
        # write the 'down' model file.
        filename = os.path.join(BLOCK_MODEL_PATH, 
                               "{}_down.json".format(args.modelname))
        with open(filename, 'w') as f:
            json.dump(block_model, f, indent=4, sort_keys=False)
        del block_model

        # now fall through and create 'up' model as default.
        block_model = copy.deepcopy(BLOCK_PLATE)
        block_model['textures'] = texture
    # TODO
    
    filename = os.path.join(BLOCK_MODEL_PATH, "{}.json".format(args.modelname))
    with open(filename, 'w') as f:
        json.dump(block_model, f, indent=4, sort_keys=False)

# items
item_model = copy.deepcopy(LOOKUP_ITEM[args.type])
if args.type in ('block','pressure_plate'):
    item_model = copy.deepcopy(LOOKUP_ITEM[args.type])
    if args.type in ('block','pressure_plate'):
        parent = "{}:block/{}".format(modid, args.modelname)
        item_model['parent'] = parent
    #TODO

filename = os.path.join(ITEM_MODEL_PATH, "{}.json".format(args.modelname))
with open(filename, 'w') as f:
    json.dump(item_model, f, indent=4, sort_keys=False)

