import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

def reject_outliers_2(data, m=2):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    # print(len(data))
    return data[s < m]
    # print(len(data))
    # print('---')
    # return data
    
def graph():
    with open('sort_times_msdp_1.json', 'r') as f:
        dataset = json.load(f)
    df = pd.json_normalize(dataset['radix_sort'])
    df= df.reindex(sorted(df.columns), axis=1)

    df = df.drop(['files','read','key', 'cols'], axis=1)
    ls = [x for x in df.columns if 'times' in x]
    for i in ls:
        df[i] = df[i].apply(lambda x: np.mean(x))
    
    for i in range(6,18,2):
        try:
            name = "insertion_"+str(i)
            rname = "radix_"+str(i)
            rangename = "ranges"+str(i)
            range2name = "ranges_doubled"+str(i)
            fails = []
            plt.cla()
            sc = True
            try:
                p1 = sns.regplot(x="rows", y=name, data=df[['rows',name]].dropna(), order=2, ci=None, scatter_kws={"s": 80}, color='r', label=name, scatter=sc)
                None
            except:                
                fails.append('insertion')
            try:
                p2 = sns.regplot(x="rows", y=rname, data=df[['rows',rname]].dropna(), order=2, ci=None, scatter_kws={"s": 80}, color = 'b', label=rname, scatter=sc)
                None
            except:
                fails.append('radix')
            try:
                p3 = sns.regplot(x="rows", y=rangename, data=df[['rows',rangename]].dropna(), order=2, ci=None, scatter_kws={"s": 80}, color = 'g', label=rangename, scatter=sc)
            except:
                fails.append('ranges')
            try:
                p4 = sns.regplot(x="rows", y=range2name, data=df[['rows',range2name]].dropna(), order=2, ci=None, scatter_kws={"s": 80}, color = 'y', label=range2name, scatter=sc)
            except:
                fails.append('ranges_doubled')
            if fails != []:
                print('fails: ' + str(fails) +' base: '+ str(i))
            if len(fails)<4:
                try:
                    plt.legend(fontsize=10)

                    plt.savefig('a_msdpgraphs/msd_pig_'+str(i)+'.jpg')
                except:
                    None
        except:
            print('fail' + str(i))
    #print(ax1 == ax2)  # True
graph()