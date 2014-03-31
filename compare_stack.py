#!/usr/bin/env python

import argparse
import style
import fnmatch
from ROOT import *

parser = argparse.ArgumentParser(description="Create stacked histograms comparing different files.")
parser.add_argument('input', metavar='INPUT', nargs='+', help='Input ROOT files to stackify.')
parser.add_argument('-o','--output', metavar='OUTPUT',default=None,help='ROOT file where the output will be stored.')
parser.add_argument('-s','--style', metavar='STYLE',default=None,help='Style to apply to the histograms.')
parser.add_argument('-n','--name', metavar='NAME',default=None,help='Plot only histograms matching this.')
parser.add_argument('-d','--dir', metavar='DIR',default=None,help='TDirectory where to start the search.')

args = parser.parse_args()

o=TFile.Open(args.output,'RECREATE') if args.output!=None else None
s=style.Style(args.style)
name_match=args.name

def get_hists(f,prefix=[]):
    hists=[]
    keys=f.GetListOfKeys()
    for key in keys:
        name=key.GetName()
        obj=f.Get(name)
        if obj.InheritsFrom("TDirectoryFile"):
            hists+=get_hists(obj,prefix+[name])
        elif obj.InheritsFrom("TH1"):
            hists.append('/'.join(prefix+[name]))
    return hists

hstacks={}
fs=[]
for input in args.input:
    parts=input.split(':')
    input=parts[0]
    extrainfo={}
    for extra in parts[1:]:
        extraparts=extra.split('=')
        key=extraparts[0]
        value='='.join(extraparts[1:])
        extrainfo[key]=value
    
    f=TFile.Open(input)
    d=f if args.dir==None else f.Get(args.dir)

    hists=get_hists(d)
    for histname in hists:
        if name_match!=None and not fnmatch.fnmatch(histname,name_match): continue
        print histname
        hist=d.Get(histname)
        histname=histname.replace('/','_')
        if histname not in hstacks:
            hstack=THStack()
            hstack.SetName(histname)

            xtitle=hist.GetXaxis().GetTitle()
            hstack.SetTitle(';%s;'%xtitle)

            hstacks[histname]=hstack

        if s!=None: s.apply_style(hist,extrainfo)
        hstacks[histname].Add(hist,hist.GetOption())            
        
    fs.append(f)

c=TCanvas()
c.SetLogy(True)
if o!=None: o.cd()
    
for name,hstack in hstacks.items():
    c.Clear()
    hstack.Draw('nostack')
    hstack.Write()
    c.SaveAs('%s.pdf'%name)

if o!=None: o.Close()

for f in fs:
    f.Close()

