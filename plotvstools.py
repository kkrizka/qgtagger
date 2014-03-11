import sys
import re
import argparse
import fnmatch
from ROOT import *

import binningtools

class PlotVs:
    def __init__(self,argv,xaxis,calc,name,ytitle=None):
        parser=argparse.ArgumentParser(description='Plot vs something')
        parser.add_argument('input',metavar='output.root',type=str,help='comparevariables output ROOT')
        parser.add_argument('output',metavar='graphs.root',nargs='?',type=str,help='where to store the output ROOT')
        parser.add_argument('--name',metavar='name',type=str,default=None,help='Name of histograms to draw. (wildcards allowed)')
        parser.add_argument('--yrange',metavar='yrange',type=str,default=None,help='The y-range (variable range) in format min:max.')
        parser.add_argument('--logy',action='store_true',default=False,help='Set y-axis to log scale.')
        args=parser.parse_args()

        self.input=args.input
        self.output=args.output

        self.name_match=args.name

        self.xaxis=xaxis # What to plot against

        self.gs={}
        self.gs_particle={}
        self.gs_idx={}
        self.ytitles={}
        self.yranges={}
        
        self.calc=calc
        self.name=name
        self.ytitle=None

        # y-range..
        self.yrange=None
        if args.yrange!=None:
            parts=args.yrange.split(':')
            self.yrange=(float(parts[0]),float(parts[1]))

        self.variables=[]
        self.histograms=['Quarks','Gluons']

        self.c=TCanvas()
        if args.logy: self.c.SetLogy(True)

    def run(self):
        f=TFile.Open(self.input)

        for key in f.GetListOfKeys():
            name=key.GetName()

            if self.name_match!=None:
                if not fnmatch.fnmatch(name,self.name_match): continue
            
            hs=f.Get(name)

            self.process(name,hs)

        self.save()

    def process(self,name,hs):
        # Extract information about this plot
        binstmp,varname=binningtools.extract_info(name)
        bins={}
        binsorder=[]
        for bin in binstmp:
            bins[bin.name]=bin
            binsorder.append(bin.name)

        if len(self.variables)>0 and varname not in self.variables: return

        print 'process',name
        # Get what this is plotted against
        xmin,xmax=bins[self.xaxis].minval,bins[self.xaxis].maxval
        del bins[self.xaxis]
        binsorder.remove(self.xaxis)

        # Get histograms
        thehists={}
        hists=hs.GetHists()
        for hist in hists:
            if self.histograms==None or hist.GetTitle() in self.histograms:
                thehists[hist.GetTitle()]=hist

        # Key
        key=self.key_for(varname,bins,binsorder,hs,thehists)

        # Determine x range
        if xmin==None:
            xmid=xmax
            xuperr=0
            xloerr=xmax
        elif xmax==None:
            xmid=xmin*1.1
            xuperr=0
            xloerr=xmin*0.1
        else:
            xmid=(xmin+xmax)/2
            xuperr=(xmax-xmin)/2
            xloerr=(xmax-xmin)/2

        # Add point
        for particle in self.gs_particle[key]:
            h=thehists.get(particle,None)
            if h==None: continue
            #if xmid in [65.0]: continue
            y,ylo,yup=self.calc(h,hs)
            self.gs_particle[key][particle].SetPoint(self.gs_idx[key][particle],xmid,y)
            self.gs_particle[key][particle].SetPointError(self.gs_idx[key][particle],xloerr,xuperr,ylo,yup)
            self.gs_idx[key][particle]+=1
            if h!=None: self.gs_particle[key][particle].SetLineColor(h.GetLineColor())
            if h!=None: self.gs_particle[key][particle].SetMarkerColor(h.GetLineColor())

    def key_for(self,varname,bins,binsorder,hs,hists):
        # Generate the key (and title)
        keys=[]
        titles=[]
        for binname in binsorder:
            range=bins[binname]
            keys.append(bins[binname].to_code())
            titles.append(bins[binname].to_title())
        keys.append(varname if self.name==None else self.name(varname))
        key='_'.join(keys)
        title=' and '.join(titles)

        # Create graphs if if they do not exist
        if key not in self.gs_idx:
            mg=TMultiGraph()
            print title
            mg.SetTitle(title)
            mg.SetName(key)

            self.gs_particle[key]={}
            self.gs_idx[key]={}
            
            for histname in hists:
                g=TGraphAsymmErrors()
                g.SetTitle(histname)
                g.SetLineColor(kRed)
                g.SetMarkerColor(kRed)
                g.SetMarkerStyle(21)

                #mg.Add(g)

                #l.AddEntry(g,histogram,'L')
                
                self.gs_particle[key][histname]=g
                self.gs_idx[key][histname]=0

            self.gs[key]=mg

            hs.Draw()
            if type(self.ytitle)==str:
                self.ytitles[key]='%s of %s'%(self.ytitle,hs.GetXaxis().GetTitle())
            elif self.ytitle!=None:
                self.ytitles[key]=self.ytitle(varname)
            else:
                self.ytitles[key]=hs.GetXaxis().GetTitle()
            self.yranges[key]=(hs.GetXaxis().GetXmin(),hs.GetXaxis().GetXmax()) if self.yrange==None else self.yrange

        return key


    def save(self):
        ## Draw everything
        if self.output!=None:
            f=TFile.Open(self.output,'RECREATE')
        else:
            f=None

        for name in self.gs:
            print name
            g=self.gs[name]
            ytitle=self.ytitles[name]
            yrange=self.yranges[name]


            # Add the graphs
            l=TLegend(0.65,1.,1.,1.-0.04*len(self.gs_particle[name]))
            for particle in self.gs_particle[name]:
                print particle
                gr=self.gs_particle[name][particle]
                if gr.GetN()==0: continue
                gr.Sort()
                g.Add(gr)
                l.AddEntry(gr,particle,'LP')

            # Draw
            self.c.Clear()
            g.Draw("APE")
            g.GetXaxis().SetTitle(binningtools.common_titles[self.xaxis])
            g.GetYaxis().SetTitle(ytitle)
            if yrange!='auto': g.GetYaxis().SetRangeUser(yrange[0],yrange[1])
            l.Draw()

            self.c.SaveAs('%s.pdf'%name)

            # Save to a root file
            if f!=None: g.Write()

        if f!=None: f.Close()
