import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import rcParams
import numpy as np
import pandas as pd
import json
import seaborn as sns
import itertools
from scipy import stats
import re
def reject_outliers_2(data, m=4):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev or 1.)
    return data[s < m]

def get_data(inp, threshold, maxc=500):
    #Input data#
    with open(f'sort_times/{inp}') as f:
        data = json.load(f)

    methodnames = list(data['radix_sort'][0]['times'].keys())

    meta = [['times', x] for x in methodnames]

    df = pd.json_normalize(data['radix_sort'],meta=meta)
    df = df.reindex(sorted(df.columns), axis=1)
    #Prepare Data
    df.columns = df.columns.str.replace('times.', '')
    drop = [] if threshold==False else ['cols']
    df = df.drop(drop +[ 'rows', 'data_type', 'data_size'], axis=1)
    df = df.reset_index(drop=True)
    melt = 'cols' if threshold==False else 'threshold'
    dfm = df.melt(melt, var_name='method', value_name='time')
    dfm.dropna(inplace=True)
    dfm['time'] = dfm['time'].apply(reject_outliers_2)
    dfm['time'] = dfm['time'].apply(np.mean)
    dfm['time'] = dfm['time'].astype(np.float32)
    # dfm = dfm[np.abs(stats.zscore(dfm['time'])) < 3]
    # for method in methodnames:
    #     df.update(df[method].apply(reject_outliers_2))
    #     df.update(df[method].apply(np.mean))
    #     df[method] = df[method].astype(np.float32)
    #     z = np.abs(stats.zscore(df[method]))
    #     t = 3
    #     outliers = df[z > t]
    #     # df = df.drop(outliers.index)
    #     df = df[np.abs(stats.zscore(df[method])) < 2]

    # df.fillna(-1.0, inplace=True)   
    # df.rename(columns=lambda x: re.match(r'(l|m)(sd_)(c|p)(_\d+)', x).group(0), inplace=True)
    dfm['insert'] = dfm['method'].apply(lambda x: 'always' if 'always' in x else 'never')
    dfm['method'] = dfm['method'].apply(
        lambda x: re.match(r'(l|m)(sd_)(c|p)(_\d+)', x)[0]
    )
    # a = [f'msd_p_{t}' for t in range(10, 12, 2)]
    # dfm = dfm[dfm['method'].isin(a)]
    # print(dfm[dfm['insert'].isin(['always'])])
    # print(dfm)


    if maxc:
        dfm = dfm[dfm['cols'] <= maxc]
    return dfm.astype({'method':str, 'time':np.float32})
import copy
def graph(threshold=False):
    melt = 'cols' if threshold==False else 'threshold'
    # dfms = []
    # for t in ['always', 'never']:
    #     fname = (
    #         f'{t}_insert_update_5.json'
    #     )
    #     # fname = 'thresh_insert_update_9.json'
    #     dfnew = get_data(fname, threshold)
    #     # dfnew['insert'] = t
    #     dfms.append(dfnew)

    
    # # dfms[0] = dfms[0][dfms[0][melt].isin(list(dfms[1][melt]))]
    # dfm = pd.concat(dfms)
    dfm = get_data('always_insert_update_never_insert_update_2.json', threshold)
    # print(dfm)
    gb = dfm.groupby('method')
    for group in gb.groups:
        plt.clf()
        plt.close()
        df = gb.get_group(group)
        fig, ax = plt.subplots(figsize=(15, 30))
        palette = itertools.cycle(sns.color_palette())

        # v = 200
        # dfp = df.pivot(index='cols', columns='insert', values='time')
        # dfp = dfp[v:-v]
        # # dfp = dfp[np.abs(stats.zscore(dfp['always'])) < 1.5]
        # # dfp = dfp[np.abs(stats.zscore(dfp['never'])) < 1.5]
        # idx = min(dfp.loc[np.greater(dfp['always'], dfp['never'])].index)
        # dfm = df.loc[np.logical_and(df['cols']>idx-v, df['cols']<idx+v)]
        # # print(dfm)
        # mi = dfm['time'].min()
        # ma = dfm['time'].max()        # if mi > 200:
        # dfm['c'] = pd.cut(dfm['cols'], bins=len(dfm.index)//5, labels=False)
        # dfg = dfm.groupby(['c'])
        # o = pd.DataFrame()
        # for g3 in dfg.groups:
        #     g4 = dfg.get_group(g3)
        #     dfg2 = g4.groupby(['insert'])
        #     for g2 in dfg2.groups:
        #         g5 = dfg2.get_group(g2)
        #         g5.loc[g5['c'] == g2, 'time'] = g5.loc[g5['c'] == g2, 'time'].mean()
        #         dfm.drop(g5.iloc[len(g5.index)//2])
        #     # dfm.drop(dfg.get_group(g2), inplace=True)
        #     # dfm.drop(g2[-1], inplace=True)
        # print(o)
        ax = sns.lmplot(data=df, x=melt, y='time',  hue='insert', order=2,height=10, aspect=15/10, palette=palette, line_kws={'linewidth': 5.0, 'solid_capstyle': 'round', 'path_effects' :[pe.Stroke(linewidth=7, foreground='black', alpha=0.5), pe.Normal()]})
        # ax.set(xlim=(idx-100, idx+100))
        # ax.set(ylim=(mi, ma))

        # r = df.loc[np.logical_and(df[melt] < 5000, df[melt] >=0)]
        ax.set_xlabels(melt,fontsize=20)
        ax.set_ylabels("Time",fontsize=20)
        plt.grid()
        if group in [f'msd_{x}_{t}' for t in range(2,18,2) for x in ['p']]:
            print(f'{group}_insert.jpg')
            plt.savefig(f'graphs/insertionfinal/{group}_insert2.jpg')
        # break


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
    