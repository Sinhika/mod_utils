#!/usr/bin/python3
"""
Generate blockstate jsons. Replaces old gen_blockstate_jsons.pl perl script.\

Must be run in src/main/resources/assets/<modid>/blockstates.

SYNOPSIS:

gen_blockstate_jsons.py [-h] --type
                               {simple,crop,facing,bars,doors,pane,stairs,pressure_plate,other}
                               blockname

Generate blockstates for standard block types

positional arguments:
  blockname             blockstate filename

optional arguments:
  -h, --help            show this help message and exit
  --type {simple,crop,facing,bars,doors,pane,stairs,pressure_plate,other}, -t {simple,crop,facing,bars,doors,pane,stairs,pressure_plate,other}
                        type of blockstate

"""

import sys
import os
import os.path
import argparse
import json
import copy

# TEMPLATES

BLOCK_TEMPLATE = { 'variants' : { '' : { "model" : None } } }

PRESSURE_PLATE = { 'variants' : { 
    'powered=false' : { "model" : None },
    'powered=true' : { "model" : None } 
} }

SLAB_TEMPLATE = { 'variants' : { 
    'type=bottom' : { "model" : None },
    'type=double' : { "model" : None },
    'type=top' : { "model" : None },
} }

BARS_TEMPLATE = {   "multipart": [
    { "apply": { "model": None } },
    { "when": { "north": "false", "west": "false", "south": "false", "east": "false" },
      "apply": { "model": None }
    },
    { "when": { "north": "true", "west": "false", "south": "false", "east": "false" },
      "apply": { "model": None }
    },
    { "when": { "north": "false", "west": "false", "south": "false", "east": "true" },
      "apply": { "model": None, "y": 90 }
    },
    { "when": { "north": "false", "west": "false", "south": "true", "east": "false" },
      "apply": { "model": None }
    },
    { "when": { "north": "false", "west": "true", "south": "false", "east": "false" },
      "apply": { "model": None, "y": 90 }
    },
    { "when": { "north": "true" }, 
      "apply": { "model": None } },
    { "when": { "east": "true" },
      "apply": { "model": None, "y": 90 }
    },
    { "when": { "south": "true" },
      "apply": { "model": None }
    },
    { "when": { "west": "true" },
      "apply": { "model": None, "y": 90 }
    }
] }

STAIRS_TEMPLATE = { "variants": {
    "facing=east,half=bottom,shape=straight":  { "model": None },
    "facing=west,half=bottom,shape=straight":  { "model": None, "y": 180, "uvlock": True },
    "facing=south,half=bottom,shape=straight": { "model": None, "y": 90, "uvlock": True },
    "facing=north,half=bottom,shape=straight": { "model": None, "y": 270, "uvlock": True },
    "facing=east,half=bottom,shape=outer_right":  { "model": None },
    "facing=west,half=bottom,shape=outer_right":  { "model": None, "y": 180, "uvlock": True },
    "facing=south,half=bottom,shape=outer_right": { "model": None, "y": 90, "uvlock": True },
    "facing=north,half=bottom,shape=outer_right": { "model": None, "y": 270, "uvlock": True },
    "facing=east,half=bottom,shape=outer_left":  { "model": None, "y": 270, "uvlock": True },
    "facing=west,half=bottom,shape=outer_left":  { "model": None, "y": 90, "uvlock": True },
    "facing=south,half=bottom,shape=outer_left": { "model": None },
    "facing=north,half=bottom,shape=outer_left": { "model": None, "y": 180, "uvlock": True },
    "facing=east,half=bottom,shape=inner_right":  { "model": None },
    "facing=west,half=bottom,shape=inner_right":  { "model": None, "y": 180, "uvlock": True },
    "facing=south,half=bottom,shape=inner_right": { "model": None, "y": 90, "uvlock": True },
    "facing=north,half=bottom,shape=inner_right": { "model": None, "y": 270, "uvlock": True },
    "facing=east,half=bottom,shape=inner_left":  { "model": None, "y": 270, "uvlock": True },
    "facing=west,half=bottom,shape=inner_left":  { "model": None, "y": 90, "uvlock": True },
    "facing=south,half=bottom,shape=inner_left": { "model": None },
    "facing=north,half=bottom,shape=inner_left": { "model": None, "y": 180, "uvlock": True },
    "facing=east,half=top,shape=straight":  { "model": None, "x": 180, "uvlock": True },
    "facing=west,half=top,shape=straight":  { "model": None, "x": 180, "y": 180, "uvlock": True },
    "facing=south,half=top,shape=straight": { "model": None, "x": 180, "y": 90, "uvlock": True },
    "facing=north,half=top,shape=straight": { "model": None, "x": 180, "y": 270, "uvlock": True },
    "facing=east,half=top,shape=outer_right":  { "model": None, "x": 180, "y": 90, "uvlock": True },
    "facing=west,half=top,shape=outer_right":  { "model": None, "x": 180, "y": 270, "uvlock": True },
    "facing=south,half=top,shape=outer_right": { "model": None, "x": 180, "y": 180, "uvlock": True },
    "facing=north,half=top,shape=outer_right": { "model": None, "x": 180, "uvlock": True },
    "facing=east,half=top,shape=outer_left":  { "model": None, "x": 180, "uvlock": True },
    "facing=west,half=top,shape=outer_left":  { "model": None, "x": 180, "y": 180, "uvlock": True },
    "facing=south,half=top,shape=outer_left": { "model": None, "x": 180, "y": 90, "uvlock": True },
    "facing=north,half=top,shape=outer_left": { "model": None, "x": 180, "y": 270, "uvlock": True },
    "facing=east,half=top,shape=inner_right":  { "model": None, "x": 180, "y": 90, "uvlock": True },
    "facing=west,half=top,shape=inner_right":  { "model": None, "x": 180, "y": 270, "uvlock": True },
    "facing=south,half=top,shape=inner_right": { "model": None, "x": 180, "y": 180, "uvlock": True },
    "facing=north,half=top,shape=inner_right": { "model": None, "x": 180, "uvlock": True },
    "facing=east,half=top,shape=inner_left":  { "model": None, "x": 180, "uvlock": True },
    "facing=west,half=top,shape=inner_left":  { "model": None, "x": 180, "y": 180, "uvlock": True },
    "facing=south,half=top,shape=inner_left": { "model": None, "x": 180, "y": 90, "uvlock": True },
    "facing=north,half=top,shape=inner_left": { "model": None, "x": 180, "y": 270, "uvlock": True }
} }

DOORS_TEMPLATE = {  "variants": {
    "facing=east,half=lower,hinge=left,open=false": { "model": None },
    "facing=east,half=lower,hinge=left,open=true": { "model": None, "y": 90 },
    "facing=east,half=lower,hinge=right,open=false": { "model": None },
    "facing=east,half=lower,hinge=right,open=true": { "model": None, "y": 270 },
    "facing=east,half=upper,hinge=left,open=false": { "model": None },
    "facing=east,half=upper,hinge=left,open=true": { "model": None, "y": 90 },
    "facing=east,half=upper,hinge=right,open=false": { "model": None },
    "facing=east,half=upper,hinge=right,open=true": { "model": None, "y": 270 },
    "facing=north,half=lower,hinge=left,open=false": { "model": None, "y": 270 },
    "facing=north,half=lower,hinge=left,open=true": { "model": None },
    "facing=north,half=lower,hinge=right,open=false": { "model": None, "y": 270 },
    "facing=north,half=lower,hinge=right,open=true": { "model": None, "y": 180 },
    "facing=north,half=upper,hinge=left,open=false": { "model": None, "y": 270 },
    "facing=north,half=upper,hinge=left,open=true": { "model": None },
    "facing=north,half=upper,hinge=right,open=false": { "model": None, "y": 270 },
    "facing=north,half=upper,hinge=right,open=true": { "model": None, "y": 180 },
    "facing=south,half=lower,hinge=left,open=false": { "model": None, "y": 90 },
    "facing=south,half=lower,hinge=left,open=true": { "model": None, "y": 180 },
    "facing=south,half=lower,hinge=right,open=false": { "model": None, "y": 90 },
    "facing=south,half=lower,hinge=right,open=true": { "model": None },
    "facing=south,half=upper,hinge=left,open=false": { "model": None, "y": 90 },
    "facing=south,half=upper,hinge=left,open=true": { "model": None, "y": 180 },
    "facing=south,half=upper,hinge=right,open=false": { "model": None, "y": 90 },
    "facing=south,half=upper,hinge=right,open=true": { "model": None },
    "facing=west,half=lower,hinge=left,open=false": {
      "model": None,
      "y": 180
    },
    "facing=west,half=lower,hinge=left,open=true": {
      "model": None,
      "y": 270
    },
    "facing=west,half=lower,hinge=right,open=false": {
      "model": None,
      "y": 180
    },
    "facing=west,half=lower,hinge=right,open=true": {
      "model": None,
      "y": 90
    },
    "facing=west,half=upper,hinge=left,open=false": {
      "model": None,
      "y": 180
    },
    "facing=west,half=upper,hinge=left,open=true": {
      "model": None,
      "y": 270
    },
    "facing=west,half=upper,hinge=right,open=false": {
      "model": None,
      "y": 180
    },
    "facing=west,half=upper,hinge=right,open=true": {
      "model": None,
      "y": 90
    }
}}

# command-line arguments
parser = argparse.ArgumentParser(description="Generate blockstates for standard block types")
parser.add_argument("blockname", help="blockstate filename")
parser.add_argument("--type", "-t", 
        choices=['simple', 'crop', 'facing', 'bars', 'door', 'pane', 'stairs',
                 'pressure_plate', 'slab', 'other'], 
        help="type of blockstate", required=True)

args = parser.parse_args()
#print(args);

# parse directory and make sure we are in the right place...
(head, tail) = os.path.split(os.getcwd())
if tail != 'blockstates':
    print('Warning: not in blockstates directory')
    exit()
(head, modid) = os.path.split(head)
(head, tail) = os.path.split(head)
if tail != 'assets':
    print('Warning: not in assets/{}/blockstates directory'.format(modid))
    exit()

# construct the blockstate

if args.type == 'simple':
    blockstate = copy.deepcopy(BLOCK_TEMPLATE)
    blockstate['variants']['']['model'] = "{}:block/{}".format(modid, args.blockname)
elif args.type == 'pressure_plate':
    blockstate = copy.deepcopy(PRESSURE_PLATE)
    blockstate['variants']['powered=false']['model'] = "{}:block/{}".format(modid, args.blockname)
    blockstate['variants']['powered=true']['model'] = "{}:block/{}_down".format(modid, args.blockname)
elif args.type == 'slab':
    blockstate = copy.deepcopy(SLAB_TEMPLATE)
    lblockname = args.blockname
    if lblockname.endswith('_block'):
        nn = lblockname.rindex('_block');
        lblockname = lblockname[0:nn]
    blockstate['variants']['type=bottom']['model'] = "{}:block/{}".format(modid, "{}_slab".format(lblockname))
    blockstate['variants']['type=double']['model'] = "{}:block/{}".format(modid, args.blockname)
    blockstate['variants']['type=top']['model'] = "{}:block/{}".format(modid, "{}_slab_top".format(lblockname))
elif args.type == 'bars':
    blockstate = copy.deepcopy(BARS_TEMPLATE)
    post_ends = "{}:block/{}_post_ends".format(modid, args.blockname)
    post = "{}:block/{}_post".format(modid, args.blockname)
    cap = "{}:block/{}_cap".format(modid, args.blockname)
    cap_alt = "{}:block/{}_cap_alt".format(modid, args.blockname)
    side = "{}:block/{}_side".format(modid, args.blockname)
    side_alt = "{}:block/{}_side_alt".format(modid, args.blockname)
    blockstate['multipart'][0]['apply']['model'] = post_ends
    blockstate['multipart'][1]['apply']['model'] = post
    blockstate['multipart'][2]['apply']['model'] = cap
    blockstate['multipart'][3]['apply']['model'] = cap
    blockstate['multipart'][4]['apply']['model'] = cap_alt
    blockstate['multipart'][5]['apply']['model'] = cap_alt
    blockstate['multipart'][6]['apply']['model'] = side
    blockstate['multipart'][7]['apply']['model'] = side
    blockstate['multipart'][8]['apply']['model'] = side_alt
    blockstate['multipart'][9]['apply']['model'] = side_alt

elif args.type == 'stairs':
    blockstate = copy.deepcopy(STAIRS_TEMPLATE)
    lblockname = args.blockname
    if lblockname.endswith('_stairs'):
        nn = lblockname.rindex('_stairs');
        lblockname = lblockname[0:nn]
    stairs = "{}:block/{}_stairs".format(modid, lblockname)
    inner_stairs = "{}:block/{}_inner_stairs".format(modid, lblockname)
    outer_stairs = "{}:block/{}_outer_stairs".format(modid, lblockname)
    blockstate['variants']["facing=east,half=bottom,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=west,half=bottom,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=south,half=bottom,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=north,half=bottom,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=east,half=bottom,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=west,half=bottom,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=south,half=bottom,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=north,half=bottom,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=east,half=bottom,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=west,half=bottom,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=south,half=bottom,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=north,half=bottom,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=east,half=bottom,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=west,half=bottom,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=south,half=bottom,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=north,half=bottom,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=east,half=bottom,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=west,half=bottom,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=south,half=bottom,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=north,half=bottom,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=east,half=top,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=west,half=top,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=south,half=top,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=north,half=top,shape=straight"]['model'] = stairs
    blockstate['variants']["facing=east,half=top,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=west,half=top,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=south,half=top,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=north,half=top,shape=outer_right"]['model'] = outer_stairs
    blockstate['variants']["facing=east,half=top,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=west,half=top,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=south,half=top,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=north,half=top,shape=outer_left"]['model'] = outer_stairs
    blockstate['variants']["facing=east,half=top,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=west,half=top,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=south,half=top,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=north,half=top,shape=inner_right"]['model'] = inner_stairs
    blockstate['variants']["facing=east,half=top,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=west,half=top,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=south,half=top,shape=inner_left"]['model'] = inner_stairs
    blockstate['variants']["facing=north,half=top,shape=inner_left"]['model'] = inner_stairs
    
else:
    print("Error: {} not yet implemented\n".format(args.type), file=sys.stderr)
    sys.exit()


#TODO

filename = "{}.json".format(args.blockname)
with open(filename, 'w') as f:
    json.dump(blockstate, f, indent=4, sort_keys=False)

