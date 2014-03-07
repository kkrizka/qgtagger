from ROOT import *
class Style:
    def __init__(self,infile):
        self.data={}

        self.parse(infile)

    def parse(self,infile):
        fh=open(infile)
        category=None
        for line in fh:
            line=line.strip()
            if line=='': continue
            if line[0]=='#': continue

            # New category
            if line[0]=='[':
                name=line[1:-1]
                print name
                category=StyleCategory(name)
                self.data[name]=category
                continue

            # Load into current category
            parts=line.split('=')
            key=parts[0]
            value='='.join(parts[1:])

            setattr(category,key,value)

    def apply_style(self,name,hist):
        if name not in self.data: return

        style=self.data[name]
        style.apply(hist)

class StyleCategory:
    def __init__(self,name):
        self.name=name

    def apply(self,hist):
        if hasattr(self,'title'):
            hist.SetTitle(self.title)

        if hasattr(self,'linecolor'):
            hist.SetLineColor(eval(self.linecolor))            
