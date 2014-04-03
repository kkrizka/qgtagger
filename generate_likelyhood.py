#!/usr/bin/env python

from ROOT import *

import ptetabinningtools
import binningtools

import array
import sys

import numpy as np
import array

if len(sys.argv)!=3:
    print 'usage: %s 2ddistr.root output.root'%sys.argv[0]
    sys.exit(-1)

FI=TColor.CreateGradientColorTable(3,np.array([0,0.5,1],'d'),np.array([0,1,1],'d'),np.array([0,1,0],'d'),np.array([1,0.9,0],'d'),100)
QGPallete=array.array('i',range(FI,FI+100))
gStyle.SetOptStat("");

f=TFile.Open(sys.argv[1])
fout=TFile.Open(sys.argv[2],'recreate')

c=TCanvas()
for key in f.GetListOfKeys():
    name=key.GetName()
    #if not name.startswith('pt170to210'): continue

    # Get the different attributes
    bins,varname=binningtools.extract_info(name)

    parts=varname.split('_')
    type=parts.pop(0)
    varname='_'.join(parts)

    codes='_'.join([bin.to_code() for bin in bins])

    if type!='quark': continue # Only one run per histogram

    print name

    ## Get the necessary histograms
    h2_quark=f.Get('%s_quark_%s'%(codes,varname))
    h2_gluon=f.Get('%s_gluon_%s'%(codes,varname))
    if h2_quark==None: 'WARNING: Missing quark histogram...'; continue
    if h2_gluon==None: 'WARNING: Missing gluon histogram...'; continue

    #h2_quark.Rebin2D(5,5)
    #h2_gluon.Rebin2D(5,5)
        
    for i in range(0,(h2_quark.GetNbinsX()+1)*(h2_quark.GetNbinsY()+1)+1):
        quark=h2_quark.GetBinContent(i)
        gluon=h2_gluon.GetBinContent(i)

        xbin=array.array('i',[0])
        ybin=array.array('i',[0])
        zbin=array.array('i',[0])
        h2_quark.GetBinXYZ(i,xbin,ybin,zbin)

        if quark>=0 and gluon>=0: continue
        if True:
            h2_quark.SetBinContent(i,0)
            h2_quark.SetBinError(i,0)
            h2_gluon.SetBinContent(i,0)
            h2_gluon.SetBinError(i,0)
            continue

        # Interpolate
        xbin=array.array('i',[0])
        ybin=array.array('i',[0])
        zbin=array.array('i',[0])
        h2_quark.GetBinXYZ(i,xbin,ybin,zbin)

        nn=0 if ybin[0]==h2_quark.GetNbinsY()+1 else 1
        ne=0 if xbin[0]==h2_quark.GetNbinsX()+1 else 1
        ns=0 if ybin[0]==0 else 1
        nw=0 if xbin[0]==0 else 1        

        # Quark interpolation
        qn=nn*h2_quark.GetBinContent(ybin[0]+1,xbin[0]  )
        qe=ne*h2_quark.GetBinContent(ybin[0]  ,xbin[0]+1)
        qs=ns*h2_quark.GetBinContent(ybin[0]-1,xbin[0]  )
        qw=nw*h2_quark.GetBinContent(ybin[0]  ,xbin[0]-1)
        q=(qn+qe+qs+qw)/(nn+ne+ns+nw)
        qn_err=nn*h2_quark.GetBinError(ybin[0]+1,xbin[0]  )**2
        qe_err=ne*h2_quark.GetBinError(ybin[0]  ,xbin[0]+1)**2
        qs_err=ns*h2_quark.GetBinError(ybin[0]-1,xbin[0]  )**2
        qw_err=nw*h2_quark.GetBinError(ybin[0]  ,xbin[0]-1)**2
        q=(qn+qe+qs+qw)/(nn+ne+ns+nw)
        q_err=sqrt(qn_err+qe_err+qs_err+qw_err)/(nn+ne+ns+nw)
        q=0 if q<0 else q
        q_err=0 if q<0 else q_err
        h2_quark.SetBinContent(i,q)
        h2_quark.SetBinError(i,q_err)

        # Gluon interpolation
        gn=nn*h2_gluon.GetBinContent(ybin[0]+1,xbin[0]  )
        ge=ne*h2_gluon.GetBinContent(ybin[0]  ,xbin[0]+1)
        gs=ns*h2_gluon.GetBinContent(ybin[0]-1,xbin[0]  )
        gw=nw*h2_gluon.GetBinContent(ybin[0]  ,xbin[0]-1)
        g=(gn+ge+gs+gw)/(nn+ne+ns+nw)
        gn_err=nn*h2_gluon.GetBinError(ybin[0]+1,xbin[0]  )**2
        ge_err=ne*h2_gluon.GetBinError(ybin[0]  ,xbin[0]+1)**2
        gs_err=ns*h2_gluon.GetBinError(ybin[0]-1,xbin[0]  )**2
        gw_err=nw*h2_gluon.GetBinError(ybin[0]  ,xbin[0]-1)**2
        g_err=sqrt(gn_err+ge_err+gs_err+gw_err)/(nn+ne+ns+nw)
        g=0 if g<0 else g
        g_err=0 if g<0 else g_err
        h2_gluon.SetBinContent(i,g)
        h2_gluon.SetBinError(i,0)



    if h2_quark.Integral()==0 or h2_gluon.Integral()==0:
        print 'WARNING: No data, skipping...'
        continue

    h2_quark.Scale(1./h2_quark.Integral())
    h2_gluon.Scale(1./h2_gluon.Integral())

    h2_sum=h2_quark.Clone('%s_sum_%s'%(codes,varname))
    h2_sum.Add(h2_gluon)

    h2_llh=h2_quark.Clone('%s_%s_llh'%(codes,varname))
    h2_llh.SetTitle(h2_llh.GetTitle().replace('Quarks','Quarks Fraction'))
    h2_llh.Divide(h2_quark,h2_sum,1,1,'B')
    h2_llh.SetContour(10,np.arange(0,1,0.1))

    ## Filter out certain tresholds for debugging
#    for i in range(0,(h2_quark.GetNbinsX()+1)*(h2_quark.GetNbinsY()+1)+1):
#        llh=h2_llh.GetBinContent(i)
#        if llh<0.4:
#            h2_llh.SetBinContent(i,0)
#            h2_quark.SetBinContent(i,0)
#            h2_gluon.SetBinContent(i,0)

    maximum=max(h2_quark.GetMaximum(),h2_gluon.GetMaximum())
    h2_quark.SetMaximum(maximum)
    h2_gluon.SetMaximum(maximum)

    ## Draw the likelyhoods
    gStyle.SetPalette(1)
    c.SetLogz(True)
    h2_quark.Draw("COLZ")
#    h2_llh.Draw("CONT3 SAME");
    c.SaveAs('llh-%s_%s.pdf('%(codes,varname))
    h2_gluon.Draw("COLZ")
#    h2_llh.Draw("CONT3 SAME");
    c.SaveAs('llh-%s_%s.pdf'%(codes,varname))
    
    gStyle.SetPalette(100,QGPallete)
    c.SetLogz(False)
    h2_llh.Draw("COLZ")
#    h2_llh.Draw("CONT3 SAME");
    h2_llh.GetZaxis().SetRangeUser(0,1)
    c.SaveAs('llh-%s_%s.pdf'%(codes,varname))

    # Titles
    h2_quark.Draw()
    var1=h2_quark.GetXaxis().GetTitle()
    var2=h2_quark.GetYaxis().GetTitle()

    title=' and '.join([bin.to_title() for bin in bins])

    ## Prepare the output histograms
    hs=THStack()
    hs.SetTitle('%s;%s and %s;'%(title,var1,var2))
    hs.SetName('%s_%s'%(codes,varname))

    nbins=20
    h_quark=TH1F('%s_quark_llh_%s'%(codes,varname),'Quarks',nbins,0,1.001)
    h_quark.SetLineColor(kRed)
    h_gluon=TH1F('%s_gluon_llh_%s'%(codes,varname),'Gluons',nbins,0,1.001)
    h_gluon.SetLineColor(kBlue)

    hs.Add(h_quark)
    hs.Add(h_gluon)

    ## Fill the output histograms
    xaxis=h2_llh.GetXaxis()
    xmin=xaxis.GetXmin()
    xstep=(xaxis.GetXmax()-xaxis.GetXmin())/100
    xbins=xaxis.GetNbins()
    
    yaxis=h2_llh.GetYaxis()
    ymin=yaxis.GetXmin()
    ystep=(yaxis.GetXmax()-yaxis.GetXmin())/100
    ybins=yaxis.GetNbins()

    scale=(100*100)/(xbins*ybins)

    for xidx in range(0,100):
        x=xmin+xstep*xidx
        for yidx in range(0,100):
            y=ymin+ystep*yidx

            llh=h2_llh.Interpolate(x,y)
            quark=h2_quark.Interpolate(x,y)/scale
            gluon=h2_gluon.Interpolate(x,y)/scale

            h_quark.Fill(llh,quark)
            h_gluon.Fill(llh,gluon)

    print h_quark.Integral()
    print h_gluon.Integral()

    ## Draw...
    c.Clear()
    hs.Draw("nostack HIST")
    c.SaveAs('llh-%s_%s.pdf)'%(codes,varname))

    # Save
    fout.cd()
    hs.Write()
    h2_llh.Write()

fout.Close()
