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


# command-line arguments
parser = argparse.ArgumentParser(description="Generate blockstates for standard block types")
parser.add_argument("blockname", help="blockstate filename")
parser.add_argument("--type", "-t", 
        choices=['simple', 'crop', 'facing', 'bars', 'doors', 'pane', 'stairs',
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
    lblockname = args.blockname
    if lblockname.endswith('_block'):
        nn = lblockname.rindex('_block');
        lblockname = lblockname[0:nn]
    blockstate = copy.deepcopy(SLAB_TEMPLATE)
    blockstate['variants']['type=bottom']['model'] = "{}:block/{}".format(modid, "{}_slab".format(lblockname))
    blockstate['variants']['type=double']['model'] = "{}:block/{}".format(modid, args.blockname)
    blockstate['variants']['type=top']['model'] = "{}:block/{}".format(modid, "{}_slab_top".format(lblockname))


# TODO

filename = "{}.json".format(args.blockname)
with open(filename, 'w') as f:
    json.dump(blockstate, f, indent=4, sort_keys=False)

