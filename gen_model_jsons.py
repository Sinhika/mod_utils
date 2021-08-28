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
# items
ITEM_BLOCK = { "parent" : None }
ITEM_GENERATED = { "parent": "minecraft:item/generated", "textures": {"layer0": None } }
ITEM_HANDHELD = { "parent": "minecraft:item/handheld", "textures": { "layer0": None } }
# blocks
BLOCK_BLOCK = { "parent" : "block/cube_all", "textures" : { "all" : None }}
BLOCK_PLATE = { 
    "parent" : "minecraft:block/pressure_plate_up",
    "textures" : { "texture" : None }
}
BLOCK_PLATE_DOWN = {
    "parent" : "minecraft:block/pressure_plate_down",
    "textures" : { "texture" : None }
    }
BLOCK_SLAB = {
    "parent": "minecraft:block/slab",
    "textures": { "bottom": None, "top": None, "side": None }    
}
BLOCK_SLAB_TOP = {
    "parent": "minecraft:block/slab_top",
    "textures": { "bottom": None, "top": None, "side": None }    
}

# LOOKUP TABLES FOR types => templates
LOOKUP_BLOCK = { 'block' : BLOCK_BLOCK  }

LOOKUP_ITEM = { 'block' : ITEM_BLOCK, 'pressure_plate' : ITEM_BLOCK, 'slab' : ITEM_BLOCK,
        'inventory' : ITEM_GENERATED, 'tool' : ITEM_HANDHELD, 'armor' : ITEM_GENERATED }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate block & item models as specified")
parser.add_argument("modelname", help="model filename")
parser.add_argument("--item_only", "--item", help="item model only", action="store_true")
parser.add_argument("--type", "-t", 
        choices=['block', 'crop', 'facing', 'bars', 'door', 'pane', 'stairs', 'slab',
                 'pressure_plate', 'pillar', 'log', 'machine', 'blockitem', 'bow',
                 'armor', 'tool', 'inventory'], 
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
        block_model['textures']['texture'] = texture
        # write the 'down' model file.
        filename = os.path.join(BLOCK_MODEL_PATH, 
                               "{}_down.json".format(args.modelname))
        with open(filename, 'w') as f:
            json.dump(block_model, f, indent=4, sort_keys=False)
        del block_model

        # now fall through and create 'up' model as default.
        block_model = copy.deepcopy(BLOCK_PLATE)
        block_model['textures']['texture'] = texture
    elif args.type == 'slab':
        # there are two model files for slabs
        block_model = copy.deepcopy(BLOCK_SLAB_TOP)
        stem = args.modelname
        nn = stem.rfind('_slab')
        stem = stem[0:nn]
        texture = "{}:block/{}".format(modid, stem)
        block_model['textures']['bottom'] = texture
        block_model['textures']['top'] = texture
        block_model['textures']['side'] = texture
        # write the 'slab_top' model file.
        filename = os.path.join(BLOCK_MODEL_PATH, "{}_top.json".format(args.modelname))
        with open(filename, 'w') as f:
            json.dump(block_model, f, indent=4, sort_keys=False)
        del block_model
        # now fall through and create default 'slab' model.
        block_model = copy.deepcopy(BLOCK_SLAB)
        block_model['textures']['bottom'] = texture
        block_model['textures']['top'] = texture
        block_model['textures']['side'] = texture
    # TODO
    else:
        print("{} type not yet implemented, sorry.\n".format(args.type), file=sys.stderr)
        sys.exit()

    filename = os.path.join(BLOCK_MODEL_PATH, "{}.json".format(args.modelname))
    with open(filename, 'w') as f:
        json.dump(block_model, f, indent=4, sort_keys=False)

# items
item_model = copy.deepcopy(LOOKUP_ITEM[args.type])
if args.type in ('block','pressure_plate','inventory','tool','armor','slab'):
    item_model = copy.deepcopy(LOOKUP_ITEM[args.type])
    if args.type in ('block','pressure_plate','slab'):
        parent = "{}:block/{}".format(modid, args.modelname)
        item_model['parent'] = parent
    elif args.type in ('inventory','tool','armor'):
        texture = "{}:item/{}".format(modid, args.modelname)
        item_model['textures']['layer0'] = texture
    #TODO
    else:
        print("{} type not yet implemented, sorry.\n".format(args.type), file=sys.stderr)
        sys.exit()

filename = os.path.join(ITEM_MODEL_PATH, "{}.json".format(args.modelname))
with open(filename, 'w') as f:
    json.dump(item_model, f, indent=4, sort_keys=False)

