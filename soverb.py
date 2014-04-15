#!/usr/bin/env python

from ROOT import *
import sys

import binningtools

import extracttools

if len(sys.argv)!=2:
    print 'usage: %s comparevariables.root'%sys.argv[0]
    sys.exit(-1)

gStyle.SetOptStat(0)
    
f=TFile.Open(sys.argv[1])

c=TCanvas('c1','c1',600,400)
c.Divide(1,2)
pad=c.cd(1)
pad.SetPad(0.01,0.15,0.99,0.99)
pad_ratio=c.cd(2)
pad_ratio.SetBorderSize(0)
pad_ratio.SetTopMargin(0)
pad_ratio.SetBottomMargin(0.3)
pad_ratio.SetPad(0.01,0.01,0.99,0.235)
pad_ratio.SetGridy()


for key in f.GetListOfKeys():
    name=key.GetName()
#    if name!='pt140to170_eta1.2to2.1_jetsAntiKt4TopoEMFiltered_funnyjeteta': continue
    print name

    hs=f.Get(name)
    pad.cd()
    hs.Draw("nostack")
    l=pad.BuildLegend(0.6,1.,1.,1.-0.08*len(hs.GetHists()))
    l.Draw()

    # Get histograms
    backgrounds=[]
    signal=None
    for h in hs.GetHists():
        if h.GetTitle()=='Gluons':
            signal=h
        else:
            backgrounds.append(h)
    
    pad_ratio.cd()
    sob=signal.Clone('sob')
    sob.Clear()
    for i in range(0,signal.GetNbinsX()):
        s=signal.Integral(0,i)
        b=sum([background.Integral(0,i) for background in backgrounds])
        if b>0: sob.SetBinContent(i,s/b)
        else: sob.SetBinContent(i,0)
        
    
    sob.Draw()

    # Fix sob axis info
    sob.GetXaxis().SetTitle(signal.GetXaxis().GetTitle())
    sob.GetXaxis().SetTitleSize(0.17)
    sob.GetXaxis().SetTitleOffset(0.9)
        
    sob.GetYaxis().SetTitle('s / b')
    sob.GetYaxis().SetTitleSize(0.17)
    sob.GetYaxis().SetTitleOffset(0.2)

    sob.GetXaxis().SetLabelFont(63);
    sob.GetXaxis().SetLabelSize(14);
    sob.GetYaxis().SetLabelFont(63);
    sob.GetYaxis().SetLabelSize(14);


    c.SaveAs('soverb-%s.pdf'%name)
