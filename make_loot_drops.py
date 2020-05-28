#!/usr/bin/python3
""" 
Generate a standard "drop myself on harvest" loot table json, given an input
item. Outputs are <blockname>.json loot_table files.

Must be run in src/main/resources/data/<modid>/loot_tables.blocks.

SYNOPSIS:
[insert help output here]

"""

import sys
import os
import os.path
import argparse
import json
import copy

LOOT_TABLE_TEMPLATE = { "type": "minecraft:block",
        "pools" : [ { "name" : None, "rolls" : 1,
            "entries" : [ { "type": "minecraft:item",
                            "name" : None
                            } ],
            "conditions" : [ { "condition" : "minecraft:survives_explosion"}]
            } ]
        }

# command-line arguments
parser = argparse.ArgumentParser(description="Generate standard 'drop myself' loot tables for blocks")
parser.add_argument("block_name", help="name of block (without modid) to be harvested")
args = parser.parse_args()

# parse directory and make sure we are in the right place...
# Must be run in src/main/resources/data/<modid>/loot_tables/blocks.
(head, tail) = os.path.split(os.getcwd())
if tail != 'blocks':
    print('Warning: not in loot_tables/blocks directory')
    sys.exit()
(head, tail) = os.path.split(head)
if tail != 'loot_tables':
    print('Warning: not in loot_tables/blocks directory')
    sys.exit()
(head, modid) = os.path.split(head)
(head, tail) = os.path.split(head)
if tail != 'data':
    print('Warning: not in data/{}/loot_tables/blocks directory'.format(modid))
    sys.exit()


