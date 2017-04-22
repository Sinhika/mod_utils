#!/bin/bash

TOPDIR=${HOME}/Projects/Minecraft_1.10
DEVLIB=${TOPDIR}/devlibs
DEVLIB110=$DEVLIB
DEOBFLIST="SimpleCore SimpleOres2 Fusion Netherrocks"

echo "Cleaning existing 1.10 libs..."
cd ${DEVLIB}
rm -f *.jar

for D in ${DEOBFLIST}; do
    JARLIST=`ls -v -r ${TOPDIR}/${D}/build/libs/*-deobf.jar`
    JAR=`echo ${JARLIST}  | cut -d' ' -f1`
    cp -v ${JAR} .
done

cd ${TOPDIR}/SimpleOres2/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simplecore-*.jar .

cd ${TOPDIR}/Fusion/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simplecore-*.jar .
ln -v -s ${DEVLIB}/simpleores-*.jar .

cd ${TOPDIR}/Netherrocks/libs
rm -r *.jar
ln -v -s ${DEVLIB}/simplecore-*.jar .

cd ${TOPDIR}/Aesthetics/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simplecore-*.jar .
ln -v -s ${DEVLIB}/simpleores-*.jar .
ln -v -s ${DEVLIB}/fusion-*.jar .
ln -v -s ${DEVLIB}/netherrocks-*.jar .

cd ${TOPDIR}/Machines/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simplecore-*.jar .
ln -v -s ${DEVLIB}/simpleores-*.jar .

cd ${TOPDIR}/akkamaddiAdditions2/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simplecore-*.jar .
ln -v -s ${DEVLIB}/simpleores-*.jar .
ln -v -s ${DEVLIB}/fusion-*.jar .


TOPDIR=${HOME}/Projects/Minecraft_1.11
DEVLIB=${TOPDIR}/devlibs
DEOBFLIST="SimpleCore"

echo "Cleaning existing 1.11 libs..."
cd ${DEVLIB}
rm -f *.jar

for D in ${DEOBFLIST}; do
    JARLIST=`ls -v -r ${TOPDIR}/${D}/build/libs/*-deobf.jar`
    JAR=`echo ${JARLIST}  | cut -d' ' -f1`
    cp -v ${JAR} .
done

