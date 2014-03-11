#!/bin/bash


if [ ${#} != 1 ]; then
    echo "usage: ${0} input.root"
    exit -1
fi

input=${1}
inputname=$(basename ${1})

for i in $(seq 0 2); do
    ./sorted_stack.py ${input} -s styles/qgtag.style -b 2 -o plot${i}_${inputname} -d plot${i}

    ./plotvspt.py plot${i}_${inputname} plot${i}_vspt_${inputname}
    ./plotvspt-fractions.py plot${i}_${inputname} plot${i}_fractions_${inputname}
done
