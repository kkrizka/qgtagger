#!/bin/bash

if [ ${#} != 1 ]; then
    echo "usage: ${0} tag"
    exit -1
fi

tag=${1}


./compare_stack.py root/${tag}.Egamma.event.root:style=data root/${tag}.Pythia8_gammajet.event.root:style=pythia8-gammajet root/${tag}.Herwigpp_gammajet.event.root:style=herwigpp-gammajet -d plot -s styles/gammajet.style -o ${tag}.root
#./compare_stack.py root/${tag}.Egamma.event.root:style=data root/${tag}.Herwigpp_gammajet.event.root:style=herwigpp-gammajet -d plot -s styles/gammajet.style -o ${tag}.root

./hsplot.py ${tag}.root --logy --ratio=Data --ratiorange=0:2 --nostack
