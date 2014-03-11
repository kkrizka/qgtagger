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

args = parser.parse_args()

o=TFile.Open(args.output,'RECREATE') if args.output!=None else None
s=style.Style(args.style) if args.style!=None else None
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

    hists=get_hists(f)
    for histname in hists:
        if not fnmatch.fnmatch(histname,name_match): continue
        hist=f.Get(histname)
        histname=histname.replace('/','_')
        if histname not in hstacks:
            hstack=THStack()
            hstack.SetName(histname)
            hstacks[histname]=hstack
        hist.Sumw2()
        if 'style' in extrainfo: s.apply_style(extrainfo['style'],hist)
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

for f in fs:
    f.Close()

if o!=None: o.ls()    
if o!=None: o.Close()
