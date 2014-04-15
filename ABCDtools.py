from math import *

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

def calc(NA,NB,NC,ND):
    P=1-(ND/NC)*(NA/NB)
    return P
