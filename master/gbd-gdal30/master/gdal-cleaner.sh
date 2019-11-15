#!/bin/bash
VERSION="3.0.2"

tar zxf v"${VERSION}".tar.gz

mv gdal-"${VERSION}"{,-fedora} && pushd gdal-"${VERSION}"-fedora/gdal

rm data/cubewerx_extra.wkt
rm data/esri_extra.wkt
rm data/esri_Wisconsin_extra.wkt
rm data/esri_StatePlane_extra.wkt
rm data/ecw_cs.wkt

#Really necessary?
rm -r swig/php

popd


#TODO: Insert Provenance file

tar cvfJ gdal-"${VERSION}"-fedora.tar.xz gdal-"${VERSION}"-fedora
