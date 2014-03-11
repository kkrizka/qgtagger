#!/usr/bin/env python

import plotvstools
import sys
import array
from ROOT import *

def calculate(h,hs):
    if h==None: return 0,0,0

    q=array.array('d',[0,0,0])
    probSum=array.array('d',[0.25,0.5,0.75])
    h.GetQuantiles(len(q),q,probSum)#GetMean()
    print q

    # Remove that damn plot
    elbin=h.FindBin(1)
    h.SetBinContent(elbin-1,0)
    h.SetBinContent(elbin,0)
    h.SetBinContent(elbin+1,0)
    h.SetBinContent(h.GetNbinsX()+1,0)
    h.SetBinContent(0,0)
    
    maxx=h.GetMean()
    lox=0#q[0]
    upx=0#q[2]

#    binmax=h.GetMaximumBin()
#    maxy=h.GetBinContent(binmax)
#    lobin=h.FindFirstBinAbove(maxy/2)
#    upbin=h.FindLastBinAbove(maxy/2)

#    maxx=h.GetBinCenter(binmax)
#    lox=maxx-h.GetBinCenter(lobin)
#    upx=h.GetBinCenter(upbin)-maxx

    return maxx,lox,upx

def name(variable):
    return variable
    

tool=plotvstools.PlotVs(sys.argv,'pt',calculate,name)
tool.ytitle='Mean'
tool.run()
