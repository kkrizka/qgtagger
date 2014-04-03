#!/bin/env python

from ROOT import *
import sys
import argparse

import ptetabinningtools

parser=argparse.ArgumentParser(description='Plot multiple purity curves.')
parser.add_argument('input',metavar='input.txt:title:color:mcinput.txt',type=str,nargs='+',help='Textfiles with the counts in ABCD regions.')
args = parser.parse_args()

def loadABCD(path):
    if path=='': return None
    datas={}
    f=open(path)
    for line in f:
        line=line.strip()
        parts=line.split()

        parts[2:]=[float(part) for part in parts[2:]]
        etastr,ptstr,NA,NB,NC,ND=parts

        if NB==0 or NC==0: continue

        if etastr not in datas: datas[etastr]={}

        datas[etastr][ptstr]=(NA,NB,NC,ND)

    return datas


datas=[]
for input in args.input:
    parts=input.split(':')
    input=parts[0]
    title=parts[1] if len(parts)>=2 else input
    color=parts[2] if len(parts)>=3 else 'kBlack'
    mcinput=parts[3] if len(parts)>=4 else ''
    datas.append((loadABCD(input),title,eval(color),loadABCD(mcinput)))

def calc_mccorr(NA,NB,NC,ND,NAsig,NBsig,NCsig,NDsig):
    cA=NAsig/NCsig
    cB=NBsig/NCsig
    cC=NCsig/NCsig
    cD=NDsig/NCsig
    
    a=cB+cA*cD
    b=cD*NA+cA*ND-NC*cB-NB
    c=NC*NB-NA*ND
    
    d=sqrt(b**2-4*a*c)

    P=(-b-sqrt(b**2-4*a*c))/(2*a*NC) if a>0 else 1-(ND/NC)*(NA/NB)
    return P

def fill_graph(g,etadatas,mcetadatas=None):
    idx=0
    for ptstr,data in etadatas.items():
            parts=ptstr[2:].split('to')
            avgpt=0
            errptlow=0
            errpthigh=0
            if parts[0]=='':
                avgpt=float(parts[1])
            elif parts[1]=='':
                avgpt=float(parts[0])*1.2
                errptlow=float(parts[0])*0.2                
            else:
                avgpt=(float(parts[0])+float(parts[1]))/2
                errptlow=errpthigh=(float(parts[1])-float(parts[0]))/2

            NA,NB,NC,ND=data

            if NA==0 or NB==0 or NC==0 or ND==0: continue

            P=1-(ND/NC)*(NA/NB)
            print NA,'/',NB,'*',ND,'/',NC,P
            Perr=(ND/NC)*(NA/NB)*sqrt(1/NA+1/NB+1/NC+1/ND)
            if mcetadatas!=None and ptstr in mcetadatas:
                NAsig,NBsig,NCsig,NDsig=mcetadatas[ptstr]

                if NAsig==0 or NBsig==0 or NCsig==0 or NDsig==0: continue

                # Just MC the statistical error bars, since the expression
                # is too messy to do by hand
                x=0
                xx=0
                N=10000
                for trail in range(N):
                    P=calc_mccorr(NA,NB,NC,ND,NAsig,NBsig,NCsig,NDsig)
                    x+=P
                    xx+=P*P
                P=x/N
                Perr=sqrt(xx/N-(x/N)**2)

#                P=(-b-sqrt(b**2-4*a*c))/(2*a*NC) if a>0 else P
#                Perr=sqrt(berr**2+derr**2+(b+d)**2*((aerr/a)**2+1/NC))/(2*a*NC)
#                print Perr

            g.SetPoint(idx,avgpt,P)
            g.SetPointError(idx,errptlow,errpthigh,Perr,Perr)

            idx+=1

## Plot a historgram of the purities
c=TCanvas()
for etastr in datas[0][0]:
    gs=[]
    mg=TMultiGraph()
    l=TLegend(0.6,0.1,0.9,0.1+len(datas)*0.04)
    for i in range(len(datas)):
        g=TGraphAsymmErrors()
        fill_graph(g,datas[i][0][etastr],datas[i][3][etastr] if datas[i][3]!=None and etastr in datas[i][3] else None)
        g.Sort()
#        g.SetMarkerStyle(21+i)
        g.SetMarkerStyle(21)
        g.SetLineColor(datas[i][2])
        g.SetMarkerColor(datas[i][2])

        mg.Add(g)
        l.AddEntry(g,datas[i][1],'LP')

        gs.append(g)

    etatitle=ptetabinningtools.etanametotitle(etastr)

    mg.SetTitle(etatitle)
    mg.Draw("APEC")
    mg.GetXaxis().SetTitle('Leading Jet P_{T} (GeV)')
    mg.GetYaxis().SetTitle('Purity')
    mg.GetYaxis().SetRangeUser(0.6,1.05)
    l.Draw()
    c.SaveAs('plotABCD-%s.pdf'%etastr)
