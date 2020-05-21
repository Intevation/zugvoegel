#!/bin/sh

for f in *.jpg; 
do 
    echo "Checking $f ..";
    echo "${f%.*}"
    convert -size 45x45 xc:none -fill $f -draw "circle 22.5,22.5 22.5,1" ${f%.*}.png

done


