#!/usr/bin/python3
"""
Generate blockstate jsons. Replaces old gen_blockstate_jsons.pl perl script.\

Must be run in src/main/resources/assets/<modid>/blockstates.

SYNOPSIS:

"""

import sys
import os
import os.path
import argparse
import json
import copy

# TEMPLATES

BLOCK_TEMPLATE = { 'variants' : { '' : { "model" : None } } }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate blockstates for standard block types")
parser.add_argument("blockname", help="blockstate filename")
parser.add_argument("--type", "-t", choices=['simple', 'crop', 'facing', 'bars', 'doors', 'pane',
    'stairs', 'other'], help="type of blockstate", required=True)

args = parser.parse_args()
#print(args);

# parse directory and make sure we are in the right place...
(head, tail) = os.path.split(os.getcwd())
if tail != 'blockstates':
    print('Warning: not in recipes directory')
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

# TODO

filename = "{}.json".format(args.blockname)
with open(filename, 'w') as f:
    json.dump(blockstate, f, indent=4, sort_keys=False)

