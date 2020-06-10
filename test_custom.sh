#!/bin/bash
TESTDIR=./data/test/recipes
mkdir -p $TESTDIR
OLDDIR=`pwd`
cd $TESTDIR

#make_custom_recipes.py -h
make_custom_recipes.py -t shaped -p "SS ,ST , T " -k "S=minecraft:iron_ingot;T=forge:items/wooden_rod" test_axe 1
make_custom_recipes.py -t shapeless -i "foo:bar_block" -n 1 bar_ingot 9
make_custom_recipes.py -t smelting -i "minecraft:raw_beef" --xp 0.25 roast_beast 1
make_custom_recipes.py -t smoking -i "minecraft:raw_beef" --xp 0.25 roast_beast 1
make_custom_recipes.py -t campfire -i "minecraft:raw_beef" --xp 0.25 roast_beast 1
make_custom_recipes.py -t shaped -c -p "###,###,###" -k "#=foo:bar_ingot" bar_block 1
