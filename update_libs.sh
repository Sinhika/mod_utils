#!/usr/bin/bash
set +f

TOPDIR=${HOME}/Projects/Minecraft_1.10
DEVLIB=${TOPDIR}/devlibs
DEOBFLIST="SimpleCore SimpleOres2 Fusion Netherrocks"
NEEDSLIBLIST="SimpleOres2 Fusion Netherrocks Aesthetics"
IS_CYGWIN=1
if [ $IS_CYGWIN == 1 ]; then
    COPYCMD="cp -v"
else
    COPYCMD="ln -v -s"
fi
if [ ! -d ${DEVLIB} ]; then
    mkdir -p ${DEVLIB}
fi

echo "Cleaning existing libs..."
cd ${DEVLIB}
rm -f *.jar

echo "Create libs directories if needed..."
for D in ${NEEDSLIBLIST}; do
    if [ ! -d ${TOPDIR}/${D}/libs ]; then
        mkdir -p ${TOPDIR}/${D}/libs
    fi
done

for D in ${DEOBFLIST}; do
    if [ ! -d ${TOPDIR}/${D}/build/libs ]; then
        continue
    fi
    JARLIST=`ls -v -r ${TOPDIR}/${D}/build/libs/*-deobf.jar`
    JAR=`echo ${JARLIST}  | cut -d' ' -f1`
    if [ -r ${JAR} ]; then
        cp -v ${JAR} .
    fi
done
cd ${TOPDIR}/SimpleOres2/libs
rm -f *.jar
${COPYCMD} ${DEVLIB}/simplecore-*.jar .

cd ${TOPDIR}/Fusion/libs
rm -f *.jar
${COPYCMD} ${DEVLIB}/simplecore-*.jar .
${COPYCMD} ${DEVLIB}/simpleores-*.jar .

cd ${TOPDIR}/Netherrocks/libs
rm -r *.jar
${COPYCMD} ${DEVLIB}/simplecore-*.jar .

cd ${TOPDIR}/Aesthetics/libs
rm -f *.jar
${COPYCMD} ${DEVLIB}/simplecore-*.jar .
${COPYCMD} ${DEVLIB}/simpleores-*.jar .
${COPYCMD} ${DEVLIB}/fusion-*.jar .
${COPYCMD} ${DEVLIB}/netherrocks-*.jar .
