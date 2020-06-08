#!/bin/bash
TESTDIR=./data/test/recipes
mkdir -p $TESTDIR
OLDDIR=`pwd`
cd $TESTDIR

#make_custom_recipes.py -h
make_custom_recipes.py -t shaped -p "SS ,ST , T " -k "S=minecraft:iron_ingot;T=forge:items/wooden_rod" test_axe 1
