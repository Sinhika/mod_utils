#!/bin/bash
TESTDIR=./data/test/advancements/recipes
mkdir -p $TESTDIR
OLDDIR=`pwd`
cd $TESTDIR
make_recipe_advancements.py -i foo:wheat foo:bread foo:cookie foo:dough foo:pastry

