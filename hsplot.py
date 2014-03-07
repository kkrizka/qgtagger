#!/bin/env python

import sys
import time
import argparse
import fnmatch

from ROOT import *

parser=argparse.ArgumentParser(description='Convert histograms inside a ROOT file to PNG\'s.')
parser.add_argument('input',metavar='input.root',type=str,help='Path to the ROOT file.')
parser.add_argument('--name',metavar='name',type=str,default=None,help='Name of histograms to draw. (wildcards allowed)')
parser.add_argument('--title',metavar='title',type=str,default=None,help='Title to put for the drawn histogram.')
parser.add_argument('--ratio',metavar='ratio',type=str,default='',help='Plot the histograms divided by reference one at the bottom. This option should specify the title of the relative one. (THStack only)')
parser.add_argument('--xrange',metavar='xrange',type=str,default=None,help='The x-range for the plot. Format is min:max.')
parser.add_argument('--yrange',metavar='yrange',type=str,default=None,help='The y-range for the plot. Format is min:max.')
parser.add_argument('--ratiorange',metavar='ratiorange',type=str,default='',help='The y-range for the ratio plot. Format is min:max (THStack only).')
parser.add_argument('--normalize',action='store_true',default=False,help='Normalize histograms to area of 1.')
parser.add_argument('--normalizey',action='store_true',default=False,help='Normalize histograms to area of 1 in y-direction slices.')
parser.add_argument('--normalizex',action='store_true',default=False,help='Normalize histograms to area of 1 in x-direction slices.')
parser.add_argument('--logx',action='store_true',default=False,help='Set x-axis to log scale.')
parser.add_argument('--logy',action='store_true',default=False,help='Set y-axis to log scale.')
parser.add_argument('--logz',action='store_true',default=False,help='Set z-axis to log scale.')
parser.add_argument('--nostack',action='store_true',default=False,help='Stack these histograms from THStack')
parser.add_argument('-K',action='append',nargs=2,help='K factor to apply to a plot, in the form of "histogram title" K-factor.')
args = parser.parse_args()

inpath=args.input
title=args.title
ratio=args.ratio
xrange=args.xrange
yrange=args.yrange
ratiorange=args.ratiorange
name_match=args.name
normalize=args.normalize
normalizex=args.normalizex
normalizey=args.normalizey
logx=args.logx
logy=args.logy
logz=args.logz
nostack=args.nostack

## Setup the x range, if set
xrangemin=None
xrangemax=None
if xrange!=None:
    parts=xrange.split(':')
    xrangemin=float(parts[0])
    xrangemax=float(parts[1])

## Setup the y range, if set
yrangemin=None
yrangemax=None
if yrange!=None:
    parts=yrange.split(':')
    yrangemin=float(parts[0])
    yrangemax=float(parts[1])

## Setup the ratio range, if set
ratiorangemin=None
ratiorangemax=None
if ratiorange!='':
    parts=ratiorange.split(':')
    ratiorangemin=float(parts[0])
    ratiorangemax=float(parts[1])


## Setup K values
K={}
if args.K==None: args.K=[]
for k in args.K:
    K[k[0]]=float(k[1])

## Rest
inpath=sys.argv[1]

fin=TFile(inpath)

if ratio=='':
    c=TCanvas()
    pad=c
else:
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

if logx:
    pad.SetLogx(True)
if logy:
    pad.SetLogy(True)
if logz:
    pad.SetLogz(True)
    
keys=fin.GetListOfKeys()
for key in keys:
    pad.cd()
    name=key.GetName()
    if name_match!=None:
        if not fnmatch.fnmatch(name,name_match): continue
    
    obj=fin.Get(name)
    if type(obj) not in [THStack,TH2F,TH2D,TH1D,TH1F]: continue # This object is not supported
    print 'Draw %s'%name

    ## Set title
    if title!=None:
        obj.SetTitle(title)

    ## Create a list of histograms that actions should be run over
    if type(obj)==THStack:
        hists=obj.GetHists()
    else:
        hists=[]
        hists.append(obj)

    ## Normalize the histograms, if requested
    if normalize:
        for hist in hists:
            integral=hist.Integral()
            if integral>0: hist.Scale(1./integral)

    if type(obj) in [TH2F,TH2D] and normalizex:
        for hist in hists:
            for ybin in range(1,hist.GetNbinsY()+1):
                projection=hist.ProjectionX('_px',ybin,ybin)
                integral=projection.Integral()
                if integral==0: continue
                for xbin in range(1,hist.GetNbinsX()+1):
                    value=hist.GetBinContent(xbin,ybin)
                    hist.SetBinContent(xbin,ybin,value/integral)

    if type(obj) in [TH2F,TH2D] and normalizey:
        for hist in hists:
            for xbin in range(1,hist.GetNbinsX()+1):
                projection=hist.ProjectionY('_py',xbin,xbin)
                integral=projection.Integral()
                if integral==0: continue
                for ybin in range(1,hist.GetNbinsY()+1):
                    value=hist.GetBinContent(xbin,ybin)
                    hist.SetBinContent(xbin,ybin,value/integral)

    ## Multiply by a K factor
    for hist in hists:
        if hist.GetTitle() in K:
            k=K[hist.GetTitle()]
            hist.Scale(k)
    
    ## Figure out the best range so all of the events are seen on the log scale
    hist=hists[0]
    binn=hist.GetNbinsX()
    binvals=[None]*binn

    for hist in hists:
        for bin in range(binn):
            val=hist.GetBinContent(bin+1)
            if val==0: continue # 0's are like Nones
            if binvals[bin]==None:
                 binvals[bin]=val
                 continue

            if nostack:
                if val<binvals[bin]:
                    binvals[bin]=val
            else:
                binvals[bin]+=val

    minval=None
    for bin in range(binn):
        val=binvals[bin]
        if val==0 or val==None: continue # Ignore zeros since that just means automatic range


        if minval==None or val<minval:
            minval=val

#    if minval!=None:
#        obj.SetMinimum(minval)
#
#    if rangemin!=None:
#        obj.SetMinimum(rangemin)
#    if rangemax!=None:
#        obj.SetMaximum(rangemax)

    ## Draw
    if type(obj)==THStack:
        orighists=obj.GetHists()

        # Get the list of histograms with options
        hists=[]
        iter=TIter(orighists)
        while True:
            h=iter()
            if h==None: break
            hists.append((h,iter.GetOption()))

        # Sort by area
        hists=sorted(hists,key=lambda h: h[0].Integral())

        # Remove any unwanted histograms
        orighists.Clear()
        for h,opt in hists:
            print h.GetTitle()
#            if h.GetTitle()=='Charms': continue
#            if h.GetTitle()=='Bottoms': continue
            if h.Integral()==0: continue
            orighists.Add(h,opt)
        hists=obj.GetHists()

        # Draw!
        opts='nostack' if nostack else ''
        obj.Draw(opts)

        if len(obj.GetHists())>1:
            height=len(obj.GetHists())*0.04
            l=pad.BuildLegend(0.6,0.93,0.95,0.93-height)
            l.Draw()
    elif type(obj) in [TH2F,TH2D]:
        obj.Draw("COLZ")
    elif type(obj) in [TH1F,TH1D]:
        obj.Draw()

    # Axis fixes
    print xrange
    if xrange!=None: obj.GetXaxis().SetRangeUser(xrangemin,xrangemax)
    if obj.GetXaxis()!=None and obj.GetXaxis().GetLabels()!=None: obj.GetXaxis().LabelsOption('v')

    ## Draw a ratio plot if necessary
    if ratio!='':
        # Find the base plot
        relative=None
        for hist in hists:
            if hist.GetTitle()==ratio:
                relative=hist
                break
        if relative==None:
            print 'Warning: Ratio base not found for %s!'%name
            continue
        # Calculate the ratios and their spread
        hstack_ratio=THStack()
        
        xs=[]
        for hist in hists:
            if hist==relative: continue
            hist_ratio=hist.Clone('%s_ratio'%hist.GetName())
            hist_ratio.Divide(relative)
            hstack_ratio.Add(hist_ratio)
            for bin in range(1,hist_ratio.GetNbinsX()+1): # Range calc
                val=hist_ratio.GetBinContent(bin)
                if val==0: continue # don't skew values with empty bins
                xs.append(val)

        c.cd(2)
        hstack_ratio.Draw("nostack")
        hstack_ratio.GetXaxis().SetTitle(obj.GetXaxis().GetTitle())
        hstack_ratio.GetXaxis().SetTitleSize(0.17)
        hstack_ratio.GetXaxis().SetTitleOffset(0.9)
        
        hstack_ratio.GetYaxis().SetTitle('1/%s'%relative.GetTitle())
        hstack_ratio.GetYaxis().SetTitleSize(0.17)
        hstack_ratio.GetYaxis().SetTitleOffset(0.2)

        hstack_ratio.GetYaxis().SetNdivisions(5,2,1)

        hstack_ratio.GetXaxis().SetLabelFont(63);
        hstack_ratio.GetXaxis().SetLabelSize(14);
        hstack_ratio.GetYaxis().SetLabelFont(63);
        hstack_ratio.GetYaxis().SetLabelSize(14);

        # Calculate optimal y-range for the ratios such that it contains a sigmma of the spread
        xs=sorted(xs)
        if ratiorangemin==None: minval=xs[len(xs)/4]
        else: minval=ratiorangemin
        if ratiorangemax==None: maxval=xs[len(xs)*3/4]
        else: maxval=ratiorangemax
        print minval,maxval
        hstack_ratio.SetMaximum(maxval)
        hstack_ratio.SetMinimum(minval)
        if xrange!=None: hstack_ratio.GetXaxis().SetRangeUser(xrangemin,xrangemax)


        # Draw the "zero" line
        zeroline=TLine(hstack_ratio.GetXaxis().GetXmin(),1,hstack_ratio.GetXaxis().GetXmax(),1)
        zeroline.Draw()
#        c.Update()
    c.SaveAs("%s.pdf"%name)
fin.Close()
