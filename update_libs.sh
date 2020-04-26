#!/bin/bash

MC_VERSION=1.14.4
TOPDIR=${HOME}/Projects/Minecraft_1.14
MAVEN_BASE=${TOPDIR}/mcmodsrepo/mod/alexndr

#DEOBFLIST="SimpleOres2 Fusion Machines Netherrocks Aesthetics"
#deobfuscated jars are now specified in build.gradle to be deobfuscated from
#the maven repo.  devlibs is dead.
#
echo "Find obfuscated jar in maven repo and copy to run/mods dirs..."
JARLIST=`ls -v -r ${MAVEN_BASE}/simpleores/SimpleOres2/${MC_VERSION}-*/*.jar`
SIMPLEORES_JAR=`echo ${JARLIST} | cut -d' ' -f1`

cd ${TOPDIR}/Fusion/run/mods
rm -f *.jar
cp -v $SIMPLEORES_JAR .

exit

## TODO ##
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
