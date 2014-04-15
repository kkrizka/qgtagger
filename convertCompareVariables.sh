#!/bin/bash


if [ ${#} != 1 ]; then
    echo "usage: ${0} input.root"
    exit -1
fi

input=${1}
inputname=$(basename ${1})
iden=$(echo ${inputname} | cut -f 1 -d .)

export PYTHONPATH=$(pwd):${PYTHONPATH}

if [ ! -d ${iden} ]; then
    mkdir ${iden}
fi

for i in $(seq 0 2); do
    ./sorted_stack.py ${input} -s styles/qgtag.style -b 2 -o ${iden}/plot${i}_${inputname} -d plot${i}
    ./sorted_stack.py ${input} -s styles/qgtag.style -b 0 -o ${iden}/plotunbin${i}_${inputname} -d plotunbin${i}
    ./compare_stack.py ${input} -o ${iden}/prepplot${i}_${inputname} -d prepplot${i}

    ./plotvspt.py ${iden}/plot${i}_${inputname} ${iden}/plot${i}_vspt_${inputname}
    ./plotvspt-fractions.py ${iden}/plot${i}_${inputname} ${iden}/plot${i}_fractions_${inputname}
    ./plotvspt-fractions.py ${iden}/naplot${i}_${inputname} ${iden}/naplot${i}_fractions_${inputname}
done
