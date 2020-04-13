#!/bin/bash

TOPDIR=${HOME}/Projects/Minecraft_1.15
DEVLIB=${TOPDIR}/devlibs
DEVLIB110=$DEVLIB
#DEOBFLIST="SimpleOres2 Fusion Machines Netherrocks Aesthetics"
DEOBFLIST="SimpleOres2 Netherrocks"

echo "Cleaning existing 1.15 libs..."
cd ${DEVLIB}
rm -f *.jar

for D in ${DEOBFLIST}; do
    JARLIST=`ls -v -r ${TOPDIR}/${D}/build/libs/*-deobf.jar`
    JAR=`echo ${JARLIST}  | cut -d' ' -f1`
    cp -v ${JAR} .
done

cd ${TOPDIR}/Fusion/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simpleores-*.jar .

exit

cd ${TOPDIR}/Machines/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simpleores-*.jar .

cd ${TOPDIR}/Aesthetics/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simpleores-*.jar .
ln -v -s ${DEVLIB}/fusion-*.jar .
ln -v -s ${DEVLIB}/netherrocks-*.jar .

cd ${TOPDIR}/hadite/libs
rm -f *.jar
ln -v -s ${DEVLIB}/simpleores-*.jar .
ln -v -s ${DEVLIB}/fusion-*.jar .
ln -v -s ${DEVLIB}/machines-*.jar .
ln -v -s ${DEVLIB}/aesthetics-*.jar .
