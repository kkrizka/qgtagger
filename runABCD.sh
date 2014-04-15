#!/bin/bash

if [ ${#} != 1 ]; then
    echo "usage: ${0} tag"
    exit -1
fi

tag=${1}

if [ ! -d abcd-${tag} ]; then
    mkdir abcd-${tag}
fi

./flatten.py root/abcd-${tag}.Egamma.event.root -o abcd-${tag}/data.root -d abcd
./flatten.py root/abcd-${tag}.Pythia8_gammajet.event.root -o abcd-${tag}/pythia8.root -d abcd
./flatten.py root/abcd-${tag}.Herwigpp_gammajet.event.root -o abcd-${tag}/herwigpp.root -d abcd

./calcABCD.py abcd-${tag}/data.root abcd-${tag}/data.txt
./calcABCD.py abcd-${tag}/pythia8.root abcd-${tag}/pythia8.txt
./calcABCD.py abcd-${tag}/herwigpp.root abcd-${tag}/herwigpp.txt

./plotABCD.py abcd-${tag}/data.txt:Simplified:kBlack abcd-${tag}/data.txt:Corrected:kRed:abcd-${tag}/pythia8.txt

./prepareABCD.py abcd-${tag}/data.txt abcd-${tag}/pythia8.txt abcd-${tag}/purity.txt

mv plotABCD-eta*pdf abcd-${tag}/
