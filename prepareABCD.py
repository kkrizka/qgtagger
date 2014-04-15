#!/bin/env python

from ROOT import *
import sys
import argparse

import binningtools

import ABCDtools

parser=argparse.ArgumentParser(description='Plot multiple purity curves.')
parser.add_argument('input',metavar='input.txt',type=str,help='Textfile with count in ABCD regions.')
parser.add_argument('mcinput',metavar='mcinput.txt',type=str,help='Textfile with MC count in ABCD regions.')
parser.add_argument('output',metavar='output.txt',type=str,help='Textfile where to save the output.')
args = parser.parse_args()


data=ABCDtools.loadABCD(args.input)
mcdata=ABCDtools.loadABCD(args.mcinput)
output=args.output

# Save
fout=open(output,'w')
for etastr in data:
    for ptstr in data[etastr]:
        NA,NB,NC,ND=data[etastr][ptstr]
        if etastr in mcdata and ptstr in mcdata[etastr]:
            NAsig,NBsig,NCsig,NDsig=mcdata[etastr][ptstr]
            text='%s\t%s\t%s\n'%(etastr,ptstr,ABCDtools.calc_mccorr(NA,NB,NC,ND,NAsig,NBsig,NCsig,NDsig))
        else:
            text='%s\t%s\t%s\n'%(etastr,ptstr,ABCDtools.calc(NA,NB,NC,ND))
        fout.write(text)
fout.close()

