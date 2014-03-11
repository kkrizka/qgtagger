#!/usr/bin/env python

import sys
import argparse
import fnmatch
from ROOT import *

parser=argparse.ArgumentParser(description='Compare different distributions')
parser.add_argument('input',metavar='output.root',nargs='+',help='Distributions to compare')
parser.add_argument('--name',metavar='name',type=str,default=None,help='Name of histograms to draw. (wildcards allowed)')
parser.add_argument('--particle',metavar='particle',action='append',help='Name of particles to draw.')
parser.add_argument('--xrange',metavar='xrange',type=str,default=None,help='The x-range (variable range) in format min:max.')
args=parser.parse_args()

inputs=args.input
name_match=args.name
xrange=None
particles=args.particle if args.particle!=None else ['Quarks','Gluons']

if args.xrange!=None:
    parts=args.xrange.split(':')
    xrange=(float(parts[0]),float(parts[1]))

hss={}
legends={}

c=TCanvas()
for input in inputs:
    print input
    # Configure drawing
    parts=input.split(':')
    input=parts.pop(0)

    intitle=input
    inmarker=0
    inline=0
    incolor=0
    for part in parts:
        configs=part.split('=')
        code=configs.pop(0)
        val='='.join(configs)

        if code=='title': intitle=val
        if code=='marker': inmarker=eval(val)
        if code=='line': inline=eval(val)
        if code=='color': incolor=int(val)

    #
    f=TFile.Open(input)
    keys=f.GetListOfKeys()
    for key in keys:
        name=key.GetName()
        if name_match!=None and not fnmatch.fnmatch(name,name_match): continue

        hs_orig=f.Get(name)
        if type(hs_orig)!=THStack: continue
        print name

        hs=None
        isnew=False
        if name not in hss: # Create the THStack for this name
            hs=THStack()
            hss[name]=hs

            # Set titles
            hs.SetTitle(hs_orig.GetTitle())
            isnew=True

            # Make leged
            legends[name]=TLegend(0.6,0.7,1.0,0.92)
            legend=legends[name]
        else:
            hs=hss[name]
            legend=legends[name]

        # Add the histograms to this
        hists=hs_orig.GetHists()
        for hist in hists:
            scale=hist.Integral()
            if scale==0: continue
            if hist.GetTitle() not in particles: continue
            hist.Scale(1./scale)

            hist.SetMarkerStyle(inmarker)
            hist.SetMarkerColor(hist.GetLineColor())

            hist.SetLineStyle(inline)
            hist.SetLineColor(hist.GetLineColor()+incolor)

#            opt="HIST"
            opt="P HIST" if inmarker!=0 else "HIST"
            print inmarker
            print opt
            hs.Add(hist,'%s'%opt)
            legend.AddEntry(hist,'%s - %s'%(intitle,hist.GetTitle()),'LP')

        # Set titles
        if isnew:
            hs_orig.Draw()
            xtitle=hs_orig.GetXaxis().GetTitle()
            ytitle=hs_orig.GetYaxis().GetTitle()
            print xtitle,ytitle
            
            hs.Draw('nostack')
            hs.GetXaxis().SetTitle(xtitle)
            hs.GetYaxis().SetTitle(ytitle)

    f.Close()
            
            
for name,hs in hss.items():
    print name
    legend=legends[name]

    c.Clear()

    hs.Draw('nostack')
    legend.Draw()

    if xrange!=None: hs.GetXaxis().SetRangeUser(xrange[0],xrange[1])

    c.SaveAs('%s.pdf'%name)
