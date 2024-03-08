import re 
import tabulate
with open('profile_output.txt', 'r') as f:
    data= f.readlines()
reg=False
l = len('   109                                                   ')
vals = []
titles = []
for idx, i in enumerate(data):
    if len(i)==1:reg=False
    if reg:
        r = re.split(r'\s+',  i[:l].strip())   
        vals.append(r)
    if '==============================================================' in i:
        titles = data[idx-1]
        titles = re.split(r'\s{2,}',  titles.strip())
        reg=True
code = []
with open('profile.py', 'r') as f:
    code = f.readlines()
for idx, val in enumerate(vals):
    while len(val)<len(titles)-1:
        vals[idx].append('')
    for i in range(2,4):
        if val[i]!='':
            vals[idx][i]=str(round(float(val[i])/1000,1))
    codeline = code[int(val[0])-1].rstrip()
    if idx==0:
        spaces = len(codeline)-len(codeline.lstrip())
    code[int(val[0])-1] =codeline[spaces:]    
    vals[idx].append('')
print(vals)
tabulate.PRESERVE_WHITESPACE = True
latex = (tabulate.tabulate(vals, tablefmt='latex'))
cdx = 0
for i in latex.splitlines():
    if r'\\' in i:
        cdx = int(i[:4].lstrip()) - 1
        ccode=code[cdx].rstrip()
        cspaces = len(ccode)-len(ccode.lstrip())
        i = i.replace(r'\\', '\;'*cspaces+'\lstinline{'+ccode + r'}\\').replace('%', '\%').replace('\lstinline{}','')
        print(i)