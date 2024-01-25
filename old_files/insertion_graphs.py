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
    with open('insertion3.json', 'r') as f:
        dataset = json.load(f)
    df = pd.json_normalize(dataset['radix_sort'])
    df= df.reindex(sorted(df.columns), axis=1)

    df = df.drop(['rows','data_type', 'cols'], axis=1)
    #print(df)
    ls = [x for x in df.columns if 'times' in x]
    #df.drop(index=df.index[:65], axis=0, inplace=True)
    for i in ls:
        df[i] = df[i].apply(reject_outliers_2)
        df[i] = df[i].apply(lambda x: np.mean(x))


    gb = df.groupby(['data_size'])
    for group in gb.groups:
        df2 = gb.get_group(group)
        for i in range(6,18,2):
            for j in ['p', 'c']:
                try:
                    fails = []
                    plt.cla()
                    sc = True
                    xname = "times.msd_"+j+'_'+str(i)
                    df2 = df2.rename(columns={xname: "msd_"+j+'_'+str(i)})
                    xname = "msd_"+j+'_'+str(i)
                    try:
                        p1 = sns.regplot(x='threshold', y=xname, data=df2, order=2, ci=None, scatter_kws={"s": 80}, color='r', label=xname, scatter=sc)
                        
                    except:                
                        fails.append(xname)
                    if fails != []:
                        print('fails: ' + str(fails))
                    if len(fails)<1:
                        try:
                            plt.legend(fontsize=10)
                            plt.savefig('thresholdgraphs/insertion'+group+xname+'.jpg')
                        except:
                            None
                except:
                    print('fail' + str(i)+j)
    #print(ax1 == ax2)  # True
graph()