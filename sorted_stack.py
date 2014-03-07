#!/usr/bin/env python

import argparse
import style
from ROOT import *

parser = argparse.ArgumentParser(description="Create stacked histograms comparing different distributions.")
parser.add_argument('input', metavar='INPUT',help='Input ROOT file to stackify.')
parser.add_argument('-d','--dir', metavar='DIR',default=None,help='TDirectory where to start the search.')
parser.add_argument('-b','--bin', metavar='BINDEPTH',default=0,type=int,help='Number of directories corresponding to bins.')
parser.add_argument('-o','--output', metavar='OUTPUT',default=None,help='ROOT file where the output will be stored.')
parser.add_argument('-s','--style', metavar='STYLE',default=None,help='Style to apply to the histograms.')

args = parser.parse_args()

def make_hists(dir,prefix):
    stacks={}
    
    keys=dir.GetListOfKeys()
    for key in keys:
        name=key.GetName()

        dir1=dir.Get(name)
        if type(dir1)!=TDirectoryFile: continue
        print 'Histogram:',name

        prefix1=prefix+[name]
        keys1=dir1.GetListOfKeys()
        for key1 in keys1:
            name1=key1.GetName()

            obj=dir1.Get(name1)

            if type(obj)!=TH1F: continue
            hist=obj

            thename='_'.join(prefix+[name1])
            if thename not in stacks:
                stack=THStack()
                stack.SetName(thename)

                xtitle=hist.GetXaxis().GetTitle()
                stack.SetTitle(';%s;'%xtitle)

                stacks[thename]=stack

            if s!=None: s.apply_style(name,hist)
            stacks[thename].Add(hist)

    print stacks.keys()
    for name,stack in stacks.items():
        print stack.GetName()
        if o!=None: stack.Write()
        c.Clear()
        stack.Draw("nostack")
        l=c.BuildLegend()
        l.Draw()
        print l
        c.SaveAs("%s.pdf"%stack.GetName())
    
def process_dir(dir,prefix,depth):
    keys=dir.GetListOfKeys()
    for key in keys:
        name=key.GetName()
        dir1=dir.Get(name)
        if type(dir1)!=TDirectoryFile: continue

        prefix1=prefix+[name]
        
        if depth==1:
            make_hists(dir1,prefix1)
        else:
            process_dir(dir1,prefix1,depth-1)


c=TCanvas()
f=TFile.Open(args.input);
d=f if args.dir==None else f.Get(args.dir)
b=args.bin
o=TFile.Open(args.output,'RECREATE') if args.output!=None else None
s=style.Style(args.style) if args.style!=None else None

process_dir(d,[],b)

if o!=None: o.Close()
