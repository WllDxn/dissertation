import pandas as pd
import itertools
import time
# import pandas as pd
def entry_point():
    ts = []
    for _, i in itertools.product(range(10), range(1, 1001)):
        with open(f'/home/will/dissertation/minor_files/compareCompiledArrs/arr{str(i)}.txt', 'r') as f:
            # while True:
            curr = [int(x) for x in f.read().split(',') if x != '']
        t = time.time()
        curr.sort()
        t1 = round(time.time()-t,6)
        print(("%.6f" % t1)+  '    '+str(len(ts)),end='\r')
        ts.append(t1)
        with open('compiledtest.txt','a+') as f:
            f.write(("%.6f" % t1))
            f.write(',')
    s = sum(ts)
    print('---------\nAverage: '+str(s/len(ts)))




    return 0
def getarrs(n):
    with open(f'{n}compiledtest.txt', 'r') as f:
        arr = list(map(float, f.read().split(',')[:-1]))
    return arr
        
def analysis():
    # arrs = [getarrs(n) for n in ['','non']]
    with open('/home/will/dissertation/minor_files/compiledtest.json','r+') as f:
        j = json.load(f)
        print(len(j['noncompiled']))
        d = pd.json_normalize(j)
        df = d.explode(d.columns.to_list())
        print(df.agg(['mean','std'])[['compiled','noncompiled']].to_latex(index=True,

                  formatters={"name": str.upper},
                
                  float_format="{:.4}".format,))
import json
def caller():
    import subprocess
    for k in range(10):
        data = {'compiled':[],'noncompiled':[], 'compiled-perf':[]}
        for i in range(1,1001):
            # p = subprocess.Popen(['/home/will/dissertation/pypy_misc/pypy3.10-v7.3.15-src/pypy/goal/tests-c',str(i)],stdout=subprocess.PIPE)
            # t1 = float(p.communicate()[0].strip())
            # data['noncompiled'].append(t1)
            t1=0.0
            p = subprocess.Popen(['/home/will/dissertation/pypy_versions/lsd_c_10_production/bin/pypy','/home/will/dissertation/minor_files/pypytest_sorter.py',str(i)],stdout=subprocess.PIPE)
            t2 = float(p.communicate()[0].strip())
            data['compiled-perf'].append(t2)
            print(f'\033[2KItem: {i+(k*1000)} noncompiled:{"%.6f" % t1}, compiled:{"%.6f" % t2}',end='\r')
        with open('compiledtest.json','r+') as f:
            if f.read() == '':
                print(1)
                newdata = {'compiled':[],'noncompiled':[], 'compiled-perf':[]}
            else:
                print(2)
                f.seek(0)
                newdata = json.load(f)
            for key in newdata.keys():
                newdata[key] += data[key]
            f.seek(0)
            json.dump(newdata,f,indent = 6)
analysis()