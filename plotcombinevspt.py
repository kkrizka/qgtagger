#!/usr/bin/env python

import sys
import re
import os.path
import array
import argparse

from ROOT import *

import ptetabinningtools

parser=argparse.ArgumentParser(description='Combine a few plotvspt outputs.')
parser.add_argument('input',metavar='graph.root',nargs='+',type=str,help='Path to the ROOT file.')
parser.add_argument('--logy',action='store_true',default=False,help='Set y-axis to log scale.')
parser.add_argument('--ratio',action='store_true',default=False,help='Add ratio plot.')
parser.add_argument('--ratiorange',metavar='ratiorange',type=str,default=None,help='The y-range for the ratio plot. Format is min:max (THStack only).')
parser.add_argument('--ratiotitle',metavar='ratiotitle',type=str,default='',help='The title for the yaxis of the ratio plot.')
parser.add_argument('--yrange',metavar='yrange',type=str,default=None,help='The y-range (variable range) in format min:max.')
args = parser.parse_args()


inputs=args.input
yrange=None
if args.yrange!=None:
    parts=args.yrange.split(':')
    yrange=(float(parts[0]),float(parts[1]))
ratio=args.ratio
ratiotitle=args.ratiotitle
ratiorange=None
if args.ratiorange!=None:
    parts=args.ratiorange.split(':')
    ratiorange=(float(parts[0]),float(parts[1]))

mgs={}
mgs_ratios={}
gs_ratiorefs={}
ref_titles={}
ls={}
ytitles={}
yranges={}

if ratio:
    c=TCanvas('c1','c1',600,600)
else:
    c=TCanvas()
for input in inputs:
    print input

    # Get configuration
    parts=input.split(':')
    input=parts.pop(0)

    intitle=input
    inmarker=20
    incolor=0
    for part in parts:
        configs=part.split('=')
        code=configs.pop(0)
        val='='.join(configs)

        if code=='title': intitle=val
        if code=='marker': inmarker=eval(val)
        if code=='color': incolor=eval(val)

    # Open and loop
    f=TFile.Open(input)
    for key in f.GetListOfKeys():
        name=key.GetName()
        #if name!='etato0.8_jet_nTrk_pv0_1GeV': continue
        g=f.Get(name)

        # Extract information
        m=re.search('eta([0-9\.]*)to([0-9\.]*)_(.*)',name)
        etamin=m.group(1)
        etamax=m.group(2)
        variable=m.group(3)
        
        # Build up the key
        key='eta%sto%s_%s'%(etamin,etamax,variable)
        print key
        
        etamin=float(etamin) if etamin!='' else None
        etamax=float(etamax) if etamax!='' else None

        # For axis and stuff
        c.Clear()
        g.Draw('APE')
        c.Update()
        
        # Create graph if it does not exist
        if key not in mgs:
            mg=TMultiGraph()
            mg.SetTitle(ptetabinningtools.etatotitle(etamin,etamax))
            mg.SetName(key)

            mg_ratios=TMultiGraph()

            l=TLegend(0.6,1.,1.,1.-0.08*len(inputs)*2)

            mgs[key]=mg
            mgs_ratios[key]=mg_ratios
            ls[key]=l
            gs_ratiorefs[key]={}

            ytitles[key]=g.GetYaxis().GetTitle()
            yranges[key]=(c.GetUymin(),c.GetUymax()) if yrange==None else (yrange[0],yrange[1])

        #Update ranges
        if yrange==None: yranges[key]=(min(c.GetUymin(),yranges[key][0]),max(c.GetUymax(),yranges[key][1]))

        # Add the graphs from the current g to the mg
        for ag in g.GetListOfGraphs():
#            if ag.GetTitle() not in ['Quarks','Gluons']: continue
            ag.SetMarkerStyle(inmarker)
            ag.SetMarkerColor(ag.GetMarkerColor())
            mgs[key].Add(ag)

            # Make ratio plots
            if ag.GetTitle() not in gs_ratiorefs[key]: # Make this the reference
                gs_ratiorefs[key][ag.GetTitle()]=ag
                ref_titles[key]=intitle
            else: # Make ratio wrt reference
                ref_x=gs_ratiorefs[key][ag.GetTitle()].GetX()
                ref_y=gs_ratiorefs[key][ag.GetTitle()].GetY()
                y=ag.GetY()
                
                g_ratio=TGraphAsymmErrors()
                g_ratio.SetLineColor(ag.GetLineColor())
                g_ratio.SetMarkerColor(ag.GetMarkerColor())
                g_ratio.SetMarkerStyle(ag.GetMarkerStyle())
                
                mgs_ratios[key].Add(g_ratio)
                
                for i in range(ag.GetN()):
                    if y[i]==0 or ref_y[i]==0:
                        g_ratio.SetPoint(i,ref_x[i],0)
                    else:
                        g_ratio.SetPoint(i,ref_x[i],y[i]/ref_y[i])
#                        g_ratio.SetPoint(i,ref_x[i],ref_y[i]/y[i])
                    g_ratio.SetPointEXhigh(i,ag.GetErrorXhigh(i))
                    g_ratio.SetPointEXlow(i,ag.GetErrorXlow(i))
                

            # Legend entry
            ls[key].AddEntry(ag,'%s - %s'%(ag.GetTitle(),intitle),'PL')

# Prepare canvas
c.Clear()

if ratio:
    c.Divide(1,2)

    pad=c.cd(1)
    pad.SetPad(0.01,0.15,0.99,0.99)
    pad_ratio=c.cd(2)
    pad_ratio.SetBorderSize(0)
    pad_ratio.SetTopMargin(0)
    pad_ratio.SetBottomMargin(0.3)
    pad_ratio.SetPad(0.01,0.01,0.99,0.235)
    pad_ratio.SetGridy()

#pad_ratio.SetPad(0.01,0.01,0.99,0.29)


# Plot
print '--- DRAW ---'
for name in mgs:
    
    print name
    mg=mgs[name]
    mg_ratios=mgs_ratios[name]
    ref_title=ref_titles[name]
    l=ls[name]
    ytitle=ytitles[name]
    yrange=yranges[name]
    
    if ratio: pad=c.cd(1)
    if args.logy: c.SetLogy(True)
    if ratio: pad.Clear()

    mg.Draw("APE")
    mg.GetXaxis().SetTitle("Jet P_{T} (GeV)")
    mg.GetYaxis().SetTitle(ytitle)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.9)
    mg.GetYaxis().SetRangeUser(yrange[0],yrange[1])
    l.Draw()

    if ratio:
        pad=c.cd(2)
        pad.Clear()
        pad.SetGridy()
        mg_ratios.Draw("APE")
    
        if mg_ratios.GetYaxis()!=None:
            if ratiorange!=None: mg_ratios.GetYaxis().SetRangeUser(ratiorange[0],ratiorange[1])
            if ratiorange!=None: mg_ratios.GetYaxis().SetNdivisions(100+int((ratiorange[1]-ratiorange[0])/0.1),False)
    
            if ratiotitle=='': mg_ratios.GetYaxis().SetTitle('1/%s'%ref_title)
            else: mg_ratios.GetYaxis().SetTitle(ratiotitle)
            #mg_ratios.GetYaxis().SetTitle('MC/Template')
            mg_ratios.GetYaxis().SetTitleSize(0.12)
            mg_ratios.GetYaxis().SetTitleOffset(0.35)
    
    
            mg_ratios.GetXaxis().SetTitle("Jet P_{T} (GeV)")
            mg_ratios.GetXaxis().SetTitleSize(0.15)
            mg_ratios.GetXaxis().SetTitleOffset(1.0)
    
            mg_ratios.GetXaxis().SetLabelFont(63);
            mg_ratios.GetXaxis().SetLabelSize(14);
            
            mg_ratios.GetXaxis().SetLabelFont(63);
            mg_ratios.GetXaxis().SetLabelSize(14);
            mg_ratios.GetYaxis().SetLabelFont(63);
            mg_ratios.GetYaxis().SetLabelSize(14);
    
            # Draw the "zero" line
            zeroline=TLine(mg_ratios.GetXaxis().GetXmin(),1,mg_ratios.GetXaxis().GetXmax(),1)
            zeroline.Draw()
    
    
#    print len(mg_ratios.GetListOfGraphs())

    c.SaveAs('%s.pdf'%name)
