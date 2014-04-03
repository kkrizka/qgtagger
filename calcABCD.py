#!/bin/env python

from ROOT import *
import sys

import ptetabinningtools

gStyle.SetOptStat('')

if len(sys.argv)!=3:
    print 'usage: %s ABCD.root output.txt'%sys.argv[0]
    sys.exit(-1)

f=TFile(sys.argv[1])
f_out=open(sys.argv[2],'w')

c=TCanvas()
c.SetLeftMargin(0.15)
c.SetLogz(True)

isomin=3e3
isomax=5e3

keys=f.GetListOfKeys()
for key in keys:
    name=key.GetName()

    if 'phtopoisolation' in name: continue
    
    plot=f.Get(name)

    parts=name.split('_')
    if len(parts)<3: continue
    ptstr=parts.pop(0)
    etastr=parts.pop(0)
#    if etastr!='eta0.8to1.2': continue
#    if etastr!='etato0.8': continue

#    print name

    ## Draw
    plot.SetTitle(plot.GetTitle()[12:])
    plot.Draw('COL')
    plot.GetXaxis().SetTitle('Isolation Energy (#DeltaR<0.4) (GeV)')
    plot.GetYaxis().SetBinLabel(1,'Tight ID')
    plot.GetYaxis().SetBinLabel(2,'Non-Tight ID')
    plot.GetYaxis().SetTitle('')
    plot.GetYaxis().LabelsOption('v')

    # Highlight areas
    A=TBox(-15e3,2,isomin,1)
    A.SetFillStyle(0)
    A.SetLineWidth(2)
    A.Draw()
    
    B=TBox(isomax,2,plot.GetXaxis().GetXmax(),1)
    B.SetFillStyle(0)
    B.SetLineWidth(2)
    B.Draw()
    
    C=TBox(-15e3,1,isomin,0)
    C.SetFillStyle(0)
    C.SetLineWidth(2)
    C.Draw()
    
    D=TBox(isomax,1,plot.GetXaxis().GetXmax(),0)
    D.SetFillStyle(0)
    D.SetLineWidth(2)
    D.Draw()
    
    ## Calculate integrals
    isomin_bin=plot.GetXaxis().FindBin(isomin)
    isomax_bin=plot.GetXaxis().FindBin(isomax)
    isolast_bin=plot.GetNbinsX()+1

    NA=plot.Integral(0,isomin_bin,2,2)
    NB=plot.Integral(isomax_bin,isolast_bin,2,2)
    NC=plot.Integral(0,isomin_bin,1,1)
    ND=plot.Integral(isomax_bin,isolast_bin,1,1)
#    print NA,NB,NC,ND
#    tot=NA+NB+NC+ND
#    NA/=tot
#    NB/=tot
#    NC/=tot
#    ND/=tot

#    print 'A,B,C,D = ',NA,NB,NC,ND
    c.SaveAs('plotABCD-%s.pdf'%name,'q')
    if NA==0 and NB==0 and NC==0 and ND==0: continue
    

    f_out.write('%s\t%s\t%E\t%E\t%E\t%E\n'%(etastr,ptstr,NA,NB,NC,ND))
