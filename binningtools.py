from SimpleAnalysis import Analysis

import re

common_titles={'mu': '< #mu >',
               'pt': 'P_{T}',
               'eta': '|#eta|'}

common_units={'mu': None,
              'pt': 'GeV',
              'eta': None}

def extract_info(name):
    re_code=re.compile(r'[a-zA-Z]+[0-9\.]*to[0-9\.]*')
    re_num=re.compile(r'[0-9]+')
    parts=name.split('_')
    bins=[]
    varname=[]
    for part in parts:
        if re_code.search(part)!=None and re_num.search(part)!=None:
            bin=Bin()
            bin.from_code(part)
            bins.append(bin)
        else: varname.append(part)

    return bins,'_'.join(varname)

def make_info(bins,varname):
    bininfo='_'.join([bin.to_code() for bin in bins])
    name='%s_%s'%(bininfo,varname)
    return name

class Bin(object):
    def __init__(self,name=None,minval=None,maxval=None,format='%0.1f'):
        self.name=name
        self.minval=minval
        self.maxval=maxval

        self.format=format

    def contains(self,value):
        if self.minval!=None and value<self.minval: return False
        if self.maxval!=None and value>=self.maxval: return False
        return True

    def from_code(self,code):
        re_code=re.compile(r'([a-zA-Z]+)([0-9\.]*)to([0-9\.]*)')
        res=re_code.search(code)

        self.name=res.group(1)
        self.minval=float(res.group(2)) if res.group(2)!='' else None
        self.maxval=float(res.group(3)) if res.group(3)!='' else None

        example=res.group(2) if res.group(2)!='' else res.group(3)
        parts=example.split('.')
        if len(parts)==1: self.format='%d'
        else:
            self.format='%%0.%df'%len(parts[1])

    def to_code(self):
        minval=(self.format%self.minval) if self.minval!=None else ''
        maxval=(self.format%self.maxval) if self.maxval!=None else ''
        return '%s%sto%s'%(self.name,minval,maxval)

    def to_title(self):
        title=common_titles.get(self.name,self.name)
        units=' '+common_units.get(self.name,'') if common_units[self.name]!=None else ''
        minval=(self.format+'%s < ')%(self.minval,units) if self.minval!=None else ''
        maxval=' < '+self.format%self.maxval+units if self.maxval!=None else ''
        return '%s%s%s'%(minval,title,maxval)


class BinningCut(Analysis.Cut):
    def __init__(self,variable,minval,maxval):
        Analysis.Cut.__init__(self)
        self.variable=variable

        self.minval=minval
        self.maxval=maxval

    def cut(self):
        value=self.variable.value()
        return value<=self.minval or value>self.maxval


class BinningVariable(Analysis.Variable):
    def __init__(self,variable,bins):
        Analysis.Variable.__init__(self,'bin_%s'%variable.name,str)

        self.variable=variable
        self.bins=bins
        
    def value(self):
        value=self.variable.value()
        for bin in self.bins:
            if bin.contains(value): return bin.to_code()
        return None

