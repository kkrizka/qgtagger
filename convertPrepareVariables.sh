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
    ./compare_stack.py ${input} -o ${iden}/prepplot${i}_${inputname} -d prepplot${i}
done
