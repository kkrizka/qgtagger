import re
# Helpers

def ptbins(defines):
    ## Binning determination
    # pt
    ptmin=None
    ptmax=None
    if 'ptcut' in defines:
        parts=defines['ptcut'].split(',')
        if parts[0]=='':
            ptmax=float(parts[1])
        elif parts[1]=='':
            ptmin=float(parts[0])
        else:
            ptmin=float(parts[0])
            ptmax=float(parts[1])
    else:
        ptmin=100
        ptmax=1000

    ## Big title determination
    # pt 
    ptmintitle=''
    ptminname=''
    ptmaxtitle=''
    ptmaxname=''
    
    if ptmin!=None:
        ptmintitle='%d GeV < '%(ptmin)
        ptminname='%d'%(int(ptmin))
    if ptmax!=None:
        ptmaxtitle=' < %d GeV'%(ptmax)
        ptmaxname='%d'%(int(ptmax))
    
    pttitle='%sP_{T}%s'%(ptmintitle,ptmaxtitle)
    ptname='pt%sto%s'%(ptminname,ptmaxname)
   
    pttitle='%sP_{T}%s'%(ptmintitle,ptmaxtitle)
    ptname='pt%sto%s'%(ptminname,ptmaxname)

    return (ptname,pttitle,ptmin,ptmax)


def etabins(defines):
    ## Binning determination
    # eta
    etamin=None
    etamax=None
    if 'etacut' in defines:
        parts=defines['etacut'].split(',')
        if parts[0]=='':
            etamax=float(parts[1])
        elif parts[1]=='':
            etamin=float(parts[0])
        else:
            etamin=float(parts[0])
            etamax=float(parts[1])
    else:
        etamax=0.8

    ## Big title determination
    # eta
    etamintitle=''
    etaminname=''
    etamaxtitle=''
    etamaxname=''
    
    if etamin!=None:
        etamintitle='%0.1f < '%(etamin)
        etaminname='%0.1f'%(etamin)
    if etamax!=None:
        etamaxtitle=' < %0.1f'%(etamax)
        etamaxname='%0.1f'%(etamax)
    
    etatitle='%s|#eta|%s'%(etamintitle,etamaxtitle)
    etaname='eta%sto%s'%(etaminname,etamaxname)

    return (etaname,etatitle,etamin,etamax)

def ptnametobins(ptstr):
    parts=ptstr[2:].split('to')
    parts=[float(part) if part!='' else None for part in parts]
    return parts

def etanametobins(etastr):
    parts=etastr[3:].split('to')
    parts=[float(part) if part!='' else None for part in parts]
    return parts

def ptnametotitle(ptstr):
    parts=ptstr[2:].split('to')
    parts=[float(part) if part!='' else '' for part in parts]
    if parts[0]=='':
        return 'P_{T} < %d GeV'%parts[1]
    elif parts[1]=='':
        return '%d GeV < P_{T}'%parts[0]
    else:
        return '%d GeV < P_{T} < %d GeV'%(parts[0],parts[1])

def etanametotitle(etastr):
    parts=etastr[3:].split('to')
    parts=[float(part) if part!='' else '' for part in parts]
    if parts[0]=='':
        return '|#eta| < %0.1f'%parts[1]
    elif parts[1]=='':
        return '%0.1f < |#eta|'%parts[0]
    else:
        return '%0.1f < |#eta| < %0.1f'%(parts[0],parts[1])

def pttotitle(ptmin,ptmax):
    if ptmin==None:
        return 'P_{T} < %0.1f GeV'%ptmax
    elif ptmax==None:
        return '%0.1f GeV < P_{T}'%ptmin
    else:
        return '%0.1f GeV < P_{T} < %0.1f GeV'%(ptmin,ptmax)

def etatotitle(etamin,etamax):
    if etamin==None:
        return '|#eta| < %0.1f'%etamax
    elif etamax==None:
        return '%0.1f < |#eta|'%etamin
    else:
        return '%0.1f < |#eta| < %0.1f'%(etamin,etamax)

def pttoname(ptmin,ptmax):
    if ptmin==None:
        return 'ptto%d'%ptmax
    elif ptmax==None:
        return 'pt%dto'%ptmin
    else:
        return 'pt%dto%d'%(ptmin,ptmax)

def etatoname(etamin,etamax):
    if etamin==None:
        return 'etato%0.1f'%etamax
    elif etamax==None:
        return 'eta%0.1fto'%etamin
    else:
        return 'eta%0.1fto%0.1f'%(etamin,etamax)

## Loaders
def load_ptetabins(filename):
    f=open(filename)
    ptbins=[]
    etabins=[]
    mode=None
    for line in f:
        line=line.strip()
        if line=='': continue
        if line=='ptcut': mode='pt'; continue
        if line=='etacut': mode='eta'; continue

        parts=line.split(',')
        bin=(None if parts[0]=='' else float(parts[0]),
             None if parts[1]=='' else float(parts[1]))
        if mode=='pt': ptbins.append(bin)
        if mode=='eta': etabins.append(bin)

    return ptbins,etabins
        
def extract_ptetabin(name):
    match=re.match('.*pt([0-9\.]*)to([0-9\.]*)_eta([0-9\.]*)to([0-9\.]*)_(.*)',name)
    if match!=None:
        ptmin=float(match.group(1)) if match.group(1)!='' else None
        ptmax=float(match.group(2)) if match.group(2)!='' else None
        etamin=float(match.group(3)) if match.group(3)!='' else None
        etamax=float(match.group(4)) if match.group(4)!='' else None
        varname=match.group(5)
    return ptmin,ptmax,etamin,etamax,varname
