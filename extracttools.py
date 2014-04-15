from ROOT import *

import numpy as np

def hs_get_histogram(hs,title):
    if hs==None: return None
    for h in hs.GetHists():
#        print h.GetTitle()
        if h.GetTitle()==title: return h
    return None

def normalize(h,area=1.):
    if h.Integral()!=0: h.Scale(area/h.Integral())

def hs_integral(hs):
    if hs==None: return 0
    integral=0
    for h in hs.GetHists():
        integral+=h.Integral()
    return integral

def list_integral(hlist):
    integral=0
    for h in hlist:
        if h!=None: integral+=h.Integral()
    return integral

def hs_getbincontent(hs,i):
    if hs==None: return 0
    bincontent=0
    for h in hs.GetHists():
        bincontent+=h.GetBinContent(i)
    return bincontent

def load_purity(path):
    puritys={}

    f=open(path)
    for line in f:
        line=line.strip()
        if line=='': continue
        parts=line.split()

        # Extract infor from line
        etastr=parts[0]
        ptstr=parts[1]
        purity=float(parts[2])

        # Save to dictionary
        key='%s_%s'%(ptstr,etastr)
        puritys[key]=purity
        
    return puritys
    
    
def extract(jetjet_data,gammajet_data,
            jetjet_mc_quark,jetjet_mc_gluon,jetjet_mc_charm,jetjet_mc_bottom,
            gammajet_mc_quark,gammajet_mc_gluon,gammajet_mc_charm,gammajet_mc_bottom,
            unpure,purity):
    # Calculate fractions
    jetjet_mc_quark_integral=jetjet_mc_quark.Integral()
    jetjet_mc_gluon_integral=jetjet_mc_gluon.Integral()
    jetjet_mc_charm_integral=jetjet_mc_charm.Integral()
    jetjet_mc_bottom_integral=jetjet_mc_bottom.Integral()
    
    gammajet_mc_quark_integral=gammajet_mc_quark.Integral()
    gammajet_mc_gluon_integral=gammajet_mc_gluon.Integral()
    gammajet_mc_charm_integral=gammajet_mc_charm.Integral()
    gammajet_mc_bottom_integral=gammajet_mc_bottom.Integral()

    jetjet_total=list_integral([jetjet_mc_quark,jetjet_mc_gluon,jetjet_mc_charm,jetjet_mc_bottom])
    if jetjet_total==0: return None
    f_q_jetjet=jetjet_mc_quark_integral/jetjet_total
    f_g_jetjet=jetjet_mc_gluon_integral/jetjet_total
    f_c_jetjet=jetjet_mc_charm_integral/jetjet_total
    f_b_jetjet=jetjet_mc_bottom_integral/jetjet_total

    gammajet_total=list_integral([gammajet_mc_quark,gammajet_mc_gluon,gammajet_mc_charm,gammajet_mc_bottom])
    if gammajet_total==0: return None
    f_q_gammajet=gammajet_mc_quark_integral/gammajet_total
    f_g_gammajet=gammajet_mc_gluon_integral/gammajet_total
    f_c_gammajet=gammajet_mc_charm_integral/gammajet_total
    f_b_gammajet=gammajet_mc_bottom_integral/gammajet_total


    # Purity information
    if unpure!=None:
        # Prepare unpure histogram
        f_unpure=1-purity

        # Modify the sizes
        f_q_gammajet*=purity
        f_g_gammajet*=purity
        f_c_gammajet*=purity
        f_b_gammajet*=purity
    else:
        f_unpure=0
    
    # Store the results here, brah
    data_quark=jetjet_mc_quark.Clone()#'%s_quark'%name)
    data_gluon=jetjet_mc_gluon.Clone()#'%s_gluon'%name)

    # Prepare the error weights
    jetjet_data.Sumw2()
    gammajet_data.Sumw2()

    # Normalize the histograms
    normalize(jetjet_data,1)
    normalize(gammajet_data,1)

    # Create the numpy matrices
    bin_data=np.matrix([[0.],
                        [0.]])

    bin_data_err=np.matrix([[0.],
                            [0.]])

    bin_quark=np.matrix([[0.],
                         [0.]])
    
    bin_gluon=np.matrix([[0.],
                         [0.]])
    
    bin_rhs_jetjet=np.matrix([[0.],
                              [0.]])
    
    bin_rhs_gammajet=np.matrix([[0.],
                                [0.]])
    
    bin_charm=np.matrix([[0.],
                         [0.]])
    
    bin_bottom=np.matrix([[0.],
                          [0.]])
    
    bin_unpure=np.matrix([[0.],
                          [0.]])
    
    bin_qgfrac=np.matrix([[0.],
                          [0.]])


    bin_qgfrac=np.matrix([[f_q_jetjet,f_g_jetjet],
                          [f_q_gammajet,f_g_gammajet]])

    bin_qgfrac_inv=np.matrix([[f_g_gammajet,-f_g_jetjet],
                              [-f_q_gammajet,f_q_jetjet]])/(f_q_jetjet*f_g_gammajet-f_g_jetjet*f_q_gammajet)

    #boi=jetjet_data.FindBin(0.08,20)
    #print 'BOI',boi

    # Loop over each of the bins
    for i in range(0,(jetjet_data.GetNbinsX()+1)*(jetjet_data.GetNbinsY()+1)):
        #print '---------------'
        bin_jetjet_data=jetjet_data.GetBinContent(i)
        bin_gammajet_data=gammajet_data.GetBinContent(i)
        #if i==boi: print 'bin content',bin_jetjet_data,bin_gammajet_data

        if bin_jetjet_data!=0 or bin_gammajet_data!=0:

            bin_jetjet_quark=jetjet_mc_quark.GetBinContent(i)/jetjet_mc_quark_integral
            bin_jetjet_gluon=jetjet_mc_gluon.GetBinContent(i)/jetjet_mc_gluon_integral
            bin_jetjet_charm=jetjet_mc_charm.GetBinContent(i)/jetjet_mc_charm_integral
            bin_jetjet_bottom=jetjet_mc_bottom.GetBinContent(i)/jetjet_mc_bottom_integral
            
            bin_gammajet_quark=gammajet_mc_quark.GetBinContent(i)/gammajet_mc_quark_integral
            bin_gammajet_gluon=gammajet_mc_gluon.GetBinContent(i)/gammajet_mc_gluon_integral
            bin_gammajet_charm=gammajet_mc_charm.GetBinContent(i)/gammajet_mc_charm_integral
            bin_gammajet_bottom=gammajet_mc_bottom.GetBinContent(i)/gammajet_mc_bottom_integral
            
            bin_unpure_val=unpure.GetBinContent(i) if unpure!=None else 0
            
            # Matrixize it
            bin_data[0]=bin_jetjet_data
            bin_data[1]=bin_gammajet_data

            bin_data_err[0]=jetjet_data.GetBinError(i)
            bin_data_err[1]=gammajet_data.GetBinError(i)
            
            bin_quark[0]=f_q_jetjet*bin_jetjet_quark
            bin_quark[1]=f_q_gammajet*bin_gammajet_quark
            
            bin_gluon[0]=f_g_jetjet*bin_jetjet_gluon
            bin_gluon[1]=f_g_gammajet*bin_gammajet_gluon
            
            bin_rhs_jetjet[0]=f_q_jetjet*bin_jetjet_quark
            bin_rhs_jetjet[1]=f_g_jetjet*bin_jetjet_gluon
            
            bin_rhs_gammajet[0]=f_q_gammajet*bin_gammajet_quark
            bin_rhs_gammajet[1]=f_g_gammajet*bin_gammajet_gluon
            
            bin_charm[0]=f_c_jetjet*bin_jetjet_charm
            bin_charm[1]=f_c_gammajet*bin_gammajet_charm
            
            bin_bottom[0]=f_b_jetjet*bin_jetjet_bottom
            bin_bottom[1]=f_b_gammajet*bin_gammajet_bottom
            
            bin_unpure[0]=0.
            bin_unpure[1]=f_unpure*bin_unpure_val
            
            # Solve this!!!
            bin_lhs=bin_data-bin_charm-bin_bottom-bin_unpure
#            bin_lhs=bin_quark+bin_gluon
            bin_rhs=bin_qgfrac_inv*bin_lhs
            
            bin_data_quark=bin_rhs[0]
            bin_data_gluon=bin_rhs[1]

            bin_data_quark_err=sqrt((bin_qgfrac_inv[0,0]*bin_data_err[0])**2+(bin_qgfrac_inv[0,1]*bin_data_err[1])**2)
            bin_data_gluon_err=sqrt((bin_qgfrac_inv[1,0]*bin_data_err[0])**2+(bin_qgfrac_inv[1,1]*bin_data_err[1])**2)

            #print i,bin_data_quark
#            if i==boi:
#                print 'BIN',i
#                print 'bin_lhs',bin_lhs
#                print 'bin_quark',bin_quark
#                print 'bin_gluon',bin_gluon
#                print 'bin_rhs',bin_rhs
#                print 'bin_data',bin_data
#                print 'bin_qg',bin_quark+bin_gluon
#                print 'from jetjet',bin_qgfrac*np.matrix([[bin_jetjet_quark],[bin_jetjet_gluon]])
#                print 'from gammajet',bin_qgfrac*np.matrix([[bin_gammajet_quark],[bin_gammajet_gluon]])
#                print bin_qgfrac
#                print bin_qgfrac_inv
#                print np.linalg.det(bin_qgfrac)
        else:
            bin_data_quark=0.
            bin_data_gluon=0.

            bin_data_quark_err=0.
            bin_data_gluon_err=0.

#        if i==boi:
#            print 'extracted'
#            print bin_data_quark,bin_data_quark_err
#            print bin_data_gluon,bin_data_gluon_err
        data_quark.SetBinContent(i,bin_data_quark)
        data_gluon.SetBinContent(i,bin_data_gluon)

        data_quark.SetBinError(i,bin_data_quark_err)
        data_gluon.SetBinError(i,bin_data_gluon_err)

    normalize(data_quark)
    normalize(data_gluon)

    return data_quark,data_gluon
