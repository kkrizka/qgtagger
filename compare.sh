#!/bin/bash

if [ ${#} != 1 ]; then
    echo "usage: ${0} tag"
    exit -1
fi

tag=${1}


./compare_stack.py root/${tag}.JetTauEtmiss.event.root:style=data root/${tag}.Pythia8_jetjet.event.root:style=pythia8-jetjet root/${tag}.Herwigpp_jetjet.event.root:style=herwigpp-jetjet root/${tag}.AlpgenJimmy_Multijet.event.root:style=alpgen-multijet -n 'plot/*' -s styles/dijet.style -o ${tag}.root

./hsplot.py ${tag}.root --logy --ratio=Data --ratiorange=0:2
