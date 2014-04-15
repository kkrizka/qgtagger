#!/bin/env python

from ROOT import *
import sys
import argparse

def hists(thedir):
    bins=[]
    for key in thedir.GetListOfKeys():
        name=key.GetName()
        if name=='cutflow': continue
        obj=thedir.Get(name)
        if type(obj)==TDirectoryFile:
            subbins=hists(obj)
            for subbin in subbins:
                bins.append(name+'/'+subbin)
        else:
            bins.append(name)
    return bins
    

parser=argparse.ArgumentParser(description='Plot trijet purity curves.')
parser.add_argument('data',metavar='data.root',type=str,help='Trijet sample in data.')
parser.add_argument('mc',metavar='mc.root',type=str,help='Trijet sample in MC.')
args = parser.parse_args()

fdata=TFile.Open(args.data)
fmc=TFile.Open(args.mc)

hsdata=fdata.Get("prepplot2")
hsmc=fmc.Get("plot2")

hs=hists(hsdata)

c=TCanvas()
for name in hs:
#    if not name.startswith('pt40to90/etato0.8'): continue
    parts=name.split('/')
    if not parts[2].endswith('funnyjeteta'): continue
    
    print name
    data=hsdata.Get(name)
    gluons=hsmc.Get('/'.join(parts[:-1]+['gluon',parts[-1]]))
    quarks=hsmc.Get('/'.join(parts[:-1]+['quark',parts[-1]]))
    charms=hsmc.Get('/'.join(parts[:-1]+['charm',parts[-1]]))
    bottoms=hsmc.Get('/'.join(parts[:-1]+['bottom',parts[-1]]))

    # Purity calculations
    g=TGraph()
    i=0
    for binidx in range(0,data.GetNbinsX()):
        ndata=data.Integral(0,binidx)

        nall=sum([h.Integral(0,binidx) for h in [gluons,quarks,charms,bottoms]])
        purity=gluons.Integral(0,binidx)/nall if nall>0 else 1
        
        g.SetPoint(i,purity,ndata)
        i+=1

    # Draw
    c.Clear()
    g.Draw("AC*")

    g.GetXaxis().SetTitle("Gluon Purity")
    g.GetYaxis().SetTitle("Number of Events")
    
    c.SaveAs("trijetpurity-%s.pdf"%'_'.join(parts))
    
