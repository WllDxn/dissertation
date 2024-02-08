import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import rcParams
import numpy as np
import pandas as pd
import json
import seaborn as sns
import itertools
from scipy import stats
def reject_outliers_2(data, m=4):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev or 1.)
    return data[s < m]

def get_data(inp, threshold, maxc=None):
    #Input data
    with open(f'sort_times/{inp}') as f:
        data = json.load(f)
    methodnames = list(data['radix_sort'][0]['times'].keys())
    meta = [['times', x] for x in methodnames]
    df = pd.json_normalize(data['radix_sort'],meta=meta)
    df = df.reindex(sorted(df.columns), axis=1)
    #Prepare Data
    df.columns = df.columns.str.replace('times.', '')
    for method in methodnames:
        df.update(df[method].apply(reject_outliers_2))
        df.update(df[method].apply(np.mean))
        df[method] = df[method].astype(np.float32)
        z = np.abs(stats.zscore(df[method]))
        t = 3
        outliers = df[z > t]
        # df = df.drop(outliers.index)
        df = df[np.abs(stats.zscore(df[method])) < 2]

    drop = [] if threshold==False else ['cols']
    melt = 'cols' if threshold==False else 'threshold'
    df = df.drop(drop +[ 'rows', 'data_type', 'data_size'], axis=1)
    df = df.reset_index(drop=True)
    # if 'always' in inp:
    #     df['t'] = df['msd_p_6']
    #     for i in range(6,18,2):
    #         df[f'msd_p_{str(i)}'] = df['t']
    #         df[f'msd_c_{str(i)}'] = df['t']
    #     df = df.drop('t', axis=1)
    if maxc:
        df = df[df['cols'] <= maxc]
    dfm = df.melt(melt, var_name='method', value_name='time')
    return dfm.astype({'method':str, 'time':np.float32})

def graph(threshold=False):
    dfms = []
    for t in ['always', 'never']:
        fname = f'{t}_insert_2.json' if t=='always' else f'{t}_insert_6.json'
        dfnew = get_data(fname, threshold)
        dfnew['insert'] = t
        dfms.append(dfnew)
    
    melt = 'cols' if threshold==False else 'threshold'
    print(dfms.loc[dfms['time' == 'always']])
    dfms[0] = dfms[0][dfms[0][melt].isin(list(dfms[1][melt]))]
    dfm = pd.concat(dfms)
    gb = dfm.groupby('method')
    for group in gb.groups:
        plt.clf()
        plt.close()
        df = gb.get_group(group)
        fig, ax = plt.subplots(figsize=(15, 30))
        palette = itertools.cycle(sns.color_palette())
        r = df
        # r = df.loc[np.logical_and(df[melt] < 5000, df[melt] >=0)]
        ax = sns.lmplot(data=r, x=melt, y='time', hue='insert', order=2,height=10, aspect=15/10, palette=palette, line_kws={'linewidth': 5.0, 'solid_capstyle': 'round', 'path_effects' :[pe.Stroke(linewidth=7, foreground='black', alpha=0.5), pe.Normal()]})
        ax.set_xlabels(melt,fontsize=20)
        ax.set_ylabels("Time",fontsize=20)
        plt.grid()
        plt.savefig(f'graphs/insertion2024/{group}_insert.jpg')
        print(f'{group}_insert.jpg')

    # for method2 in df.columns.drop('threshold'):
    #     #ax = ax.scatter(df['threshold'], df[method2], marker=".")
    #     df[method2] = df[method2].astype(np.float64)
    #     col = next(palette)
        # ax = df.plot(x='threshold', y=method2, kind='scatter', figsize=(15, 8), grid=True)
        # plt.xlabel("Threshold")
        # plt.ylabel("Times")
    

if __name__=="__main__":
    # graph('never_insert_0.json')
    graph()
    