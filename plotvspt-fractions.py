#!/usr/bin/env python

import plotvstools
import sys
from ROOT import *

def calculate(h,hs):
    if h==None: return 0,0,0
    
    total=0
    for hist in hs.GetHists():
        total+=hist.Integral()
    if total==0: return 0,0,0
    
    maxx=h.Integral()
    if maxx==0: return 0,0,0

#    print h.GetTitle(),maxx/total
    lox=upx=sqrt(1/maxx+1/total)*(maxx/total)
    lox=upx=0
#    print lox

    return maxx/total,lox,upx

def name(variable):
    return 'fractions'

def ytitle(variable):
    return 'Fraction of Events'


tool=plotvstools.PlotVs(sys.argv,'pt',calculate,name)
tool.variables.append('pt')
tool.ytitle=ytitle
tool.yrange=(0.,1.)
tool.name=name
tool.histograms=['Quarks','Gluons','Charms','Bottoms','Unlabeled']

tool.run()
