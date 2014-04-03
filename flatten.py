#!/usr/bin/env python

import argparse
import style
from ROOT import *

parser = argparse.ArgumentParser(description="Flatten directories in a ROOT file.")
parser.add_argument('input', metavar='INPUT',help='Input ROOT file to flatten.')
parser.add_argument('-d','--dir', metavar='DIR',default=None,help='TDirectory where to start the search.')
parser.add_argument('-o','--output', metavar='OUTPUT',default=None,help='ROOT file where the output will be stored.')

args = parser.parse_args()

def process_dir(dir,prefix):
    keys=dir.GetListOfKeys()
    for key in keys:
        name=key.GetName()

        dir1=dir.Get(name)
        if type(dir1)==TDirectoryFile: # continue flattening
            prefix1=prefix+[name]
            process_dir(dir1,prefix1)
        else:
            dir1.SetName('_'.join(prefix+[name]));
            dir1.Write()


c=TCanvas()
f=TFile.Open(args.input);
d=f if args.dir==None else f.Get(args.dir)
o=TFile.Open(args.output,'RECREATE') if args.output!=None else None

process_dir(d,[])

if o!=None: o.Close()
