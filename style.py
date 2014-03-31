from ROOT import *
class Style:
    def __init__(self,infile):
        self.data={}

        if infile!=None: self.parse(infile)

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
                category={}
                self.data[name]=category
                continue

            # Load into current category
            parts=line.split('=')
            key=parts[0]
            value='='.join(parts[1:])

            category[key]=value

    def apply_style(self,hist,extra={},name=None):
        data={}
        if 'style' in extra:
            hist.SetTitle(extra['style'])
            data=dict(data.items()+self.data[extra['style']].items())
        elif name!=None:
            hist.SetTitle(name)
            data=dict(data.items()+self.data[name].items())

        data=dict(data.items()+extra.items())

        if 'title' in data:
            hist.SetTitle(data['title'])

        if 'linecolor' in data:
            hist.SetLineColor(eval(data['linecolor']))            

        if 'fillcolor' in data:
            hist.SetFillColor(eval(data['fillcolor']))
            
        if 'options' in data:
            hist.SetOption(data['options'])
        else:
            hist.SetOption('HIST')
