#!/usr/bin/env python

from ROOT import *
import sys
import numpy as np

import binningtools

import extracttools

if len(sys.argv)!=5 and len(sys.argv)!=7:
    print 'usage: %s jetjet_data.root gammajet_data.root jetjet_mc.root gammajet_mc.root [purity.txt unpure.root]'%sys.argv[0]
    sys.exit(-1)

jetjet_data_fh=TFile.Open(sys.argv[1])
gammajet_data_fh=TFile.Open(sys.argv[2])
jetjet_mc_fh=TFile.Open(sys.argv[3])
gammajet_mc_fh=TFile.Open(sys.argv[4])
unpure_fh=TFile.Open(sys.argv[6]) if len(sys.argv)==7 else None
puritys=extracttools.load_purity(sys.argv[5]) if len(sys.argv)==7 else None

## Information
info=TPaveText(0.6,0.75,0.89,0.89,'bl NDC')
info.SetBorderSize(0)
info.SetFillColor(0)
info.AddText('Red: Quarks    Blue: Gluons')
#info.AddLine(0,0.5,1,0.5)
info.AddText('Solid: Herwig++ Dijet  Dashed: Herwig++ #gamma+jet')
info.AddText('Error Bars: Extracted')

## Loop over all histograms that should be extracted
c=TCanvas()
f=TFile.Open('extract.root','recreate')
for key in jetjet_data_fh.GetListOfKeys(): # 
    name=key.GetName()
    #if name!='pt170to210_etato0.8_jet_AntiKt4TopoEM_nTrk_pv0_1GeV': continue
    #if name!='pt170to210_eta1.2to2.1_jet_nTrk_pv0_1GeV': continue
    #if name!='pt170to210_eta1.2to2.1_jet_trackWIDTH_pv0_1GeV': continue
    #if 'pt170to210_eta1.2to2.1' not in name: continue    
    #if name!='pt210to410_eta2.1to2.5_jet_WIDTH': continue
    print name

    parts=name.split('_')
    key='_'.join(parts[:2])

    # Get the requested histograms
    jetjet_data_hs=jetjet_data_fh.Get(name)
    jetjet_data=jetjet_data_hs.GetHists().At(0) if jetjet_data_hs!=None else None
    gammajet_data_hs=gammajet_data_fh.Get(name)
    gammajet_data=gammajet_data_hs.GetHists().At(0) if gammajet_data_hs!=None else None

    jetjet_mc=jetjet_mc_fh.Get(name)
    jetjet_mc_quark=extracttools.hs_get_histogram(jetjet_mc,'Quarks')
    jetjet_mc_gluon=extracttools.hs_get_histogram(jetjet_mc,'Gluons')
    jetjet_mc_charm=extracttools.hs_get_histogram(jetjet_mc,'Charms')
    jetjet_mc_bottom=extracttools.hs_get_histogram(jetjet_mc,'Bottoms')

    gammajet_mc=gammajet_mc_fh.Get(name)
    gammajet_mc_quark=extracttools.hs_get_histogram(gammajet_mc,'Quarks')
    gammajet_mc_gluon=extracttools.hs_get_histogram(gammajet_mc,'Gluons')
    gammajet_mc_charm=extracttools.hs_get_histogram(gammajet_mc,'Charms')
    gammajet_mc_bottom=extracttools.hs_get_histogram(gammajet_mc,'Bottoms')

    # Skip on any missing histograms
    if jetjet_data==None: print 'Missing jetjet_data'; continue
    if gammajet_data==None: print 'Missing gammajet_data'; continue

    if jetjet_mc_quark==None: print 'Missing jetjet_mc_quark'; continue
    if jetjet_mc_gluon==None: print 'Missing jetjet_mc_gluon'; continue
    if jetjet_mc_charm==None: print 'Missing jetjet_mc_charm'; continue
    if jetjet_mc_bottom==None: print 'Missing jetjet_mc_bottom'; continue

    if gammajet_mc_quark==None: print 'Missing gammajet_mc_quark'; continue
    if gammajet_mc_gluon==None: print 'Missing gammajet_mc_gluon'; continue
    if gammajet_mc_charm==None: print 'Missing gammajet_mc_charm'; continue
    if gammajet_mc_bottom==None: print 'Missing gammajet_mc_bottom'; continue

    # Rebin
    rebin=1 # 4
    jetjet_data.Rebin(rebin)
    jetjet_mc_quark.Rebin(rebin)
    jetjet_mc_gluon.Rebin(rebin)
    jetjet_mc_charm.Rebin(rebin)
    jetjet_mc_bottom.Rebin(rebin)

    gammajet_data.Rebin(rebin)
    gammajet_mc_quark.Rebin(rebin)
    gammajet_mc_gluon.Rebin(rebin)
    gammajet_mc_charm.Rebin(rebin)
    gammajet_mc_bottom.Rebin(rebin)

    # Draw the results here, brah
    hs=THStack()
    hs.SetTitle(jetjet_mc.GetTitle())
    hs.Add(jetjet_mc_quark,'HIST')
    hs.Add(jetjet_mc_gluon,'HIST')
    hs.Add(gammajet_mc_quark,'HIST')
    hs.Add(gammajet_mc_gluon,'HIST')
    gammajet_mc_quark.SetLineStyle(2)
    gammajet_mc_gluon.SetLineStyle(2)


    data_hs=THStack()
    data_hs.SetName(jetjet_mc.GetName())
    data_hs.SetTitle(jetjet_mc.GetTitle())


    ## Purity information
    # Prepare the unpure histogram
    unpure=None
    purity=None
    if len(sys.argv)==7:
        if key in puritys:
            purity=puritys[key]
        
        # Prepare unpure histogram
        unpure=unpure_fh.Get(name)
        if unpure!=None:
            unpure=unpure.GetHists().At(0)
            extracttools.normalize(unpure,1)

        if unpure==None or purity==None:
            print 'WARNING! No purity information...'
            

    ## Aaaaand extract!
    data_quark,data_gluon=extracttools.extract(jetjet_data,gammajet_data,
                                               jetjet_mc_quark,jetjet_mc_gluon,jetjet_mc_charm,jetjet_mc_bottom,
                                               gammajet_mc_quark,gammajet_mc_gluon,gammajet_mc_charm,gammajet_mc_bottom,
                                               unpure,purity)

    ## Prepare for draw
    # Normalize the mc histograms
    jetjet_mc_quark.Scale(1./jetjet_mc_quark.Integral())
    jetjet_mc_gluon.Scale(1./jetjet_mc_gluon.Integral())
    gammajet_mc_quark.Scale(1./gammajet_mc_quark.Integral())
    gammajet_mc_gluon.Scale(1./gammajet_mc_gluon.Integral())
    
    # Style
    data_quark.SetLineColor(jetjet_mc_quark.GetLineColor()+1)
    data_quark.SetMarkerColor(jetjet_mc_quark.GetLineColor()+1)
#    data_quark.SetLineWidth(2)
    data_gluon.SetLineColor(jetjet_mc_gluon.GetLineColor()+2)
    data_gluon.SetMarkerColor(jetjet_mc_gluon.GetLineColor()+2)
#    data_gluon.SetLineWidth(2)

    # Add
    hs.Add(data_quark,'E')
    hs.Add(data_gluon,'E')

    data_hs.Add(data_quark,'E')
    data_hs.Add(data_gluon,'E')


    ## Draw
    jetjet_data.Draw()
    xtitle=jetjet_data.GetXaxis().GetTitle()
    
    hs.Draw("nostack")
    hs.GetXaxis().SetTitle(xtitle)
    info.Draw()
    c.SaveAs("extract-%s.pdf"%name)

    ## Save to file
    # Don't need thick lines
    data_hs.Draw()
    data_hs.GetXaxis().SetTitle(xtitle)
    data_quark.SetLineWidth(1)
    data_gluon.SetLineWidth(1)
    
    # Save
    f.cd()
    data_hs.Write()
