#!/bin/bash

if [ ${#} != 1 ]; then
    echo "usage: ${0} input.root"
    exit -1
fi

name=cutflow-$(basename ${1} .root)

if [ -d ${name} ]; then
    rm -rf ${name}
fi
mkdir ${name}

./sorted_stack.py ${1} -b 0 -s styles/cutflow.style -d sample -o ${name}/cutflow.root

cd ${name}
../hsplot.py cutflow.root --nostack --logy
