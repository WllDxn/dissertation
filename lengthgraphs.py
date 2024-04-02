import json
from operator import index
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
import natsort
import os
import re
pd.set_option('display.max_rows', 10)
pd.set_option('expand_frame_repr', False)
def reject_outliers(df, m=2):
    df = np.array(df)
    d = np.abs(df - np.median(df))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return df[s < m]


def get_data(fname):
    with open(fname, 'r') as f:
        dataset = json.load(f)
    df = pd.json_normalize(dataset['radix_sort'])
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.drop(['files', 'read', 'key'], axis=1, errors='ignore')
    # print(df)
    df = df.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times')
    df['implementation'] = df['method'].str.extract(r'([^\_]+$)')
    df['implementation'] = df['implementation'].str.replace("workingfinalnosort", "nosort", regex=False)
    df['implementation'] = df['implementation'].str.replace("workingfinal", "sort", regex=False)
    df[['method', 'base']] = df['method'].str.extract(r'(\D+)(\d+)')
    df["method"] = df["method"].str.replace("times.", "", regex=False)
    df['methodbase'] = df['method'] + df['base']
    df["method"] = df["method"].str[:-1]
    # df = df.melt(id_vars=['data_type', 'data_size', 'cols', 'rows', 'method', 'implementation', 'base', 'methodbase'], var_name='times', value_name='times')
    # df.drop(df[np.logical_not(df.method.str.contains('msd_p'))].index, inplace=True)
    # df.drop(df[np.logical_not(np.logical_or(np.logical_or(df.base.str.contains('10'), df.base.str.contains('12')), df.base.str.contains('14')))].index, inplace=True)
    # df = df.explode('times')
    # print(df)
    df = df.dropna()
    # print(df[np.logical_and(df['data_size'].(int)=='32', df['base'].astype(int)=='2')])
    reject = {
        'lsd_c':[2, 4,16],
        'lsd_p':[8,4,6,2],
        'msd_c':[2],
        'msd_p':[],
        # 'lsd_c':[2, 4, 6, 8, 16],
        # 'lsd_p':[2, 4, 16, 14, 8],
        # 'msd_c':[2, 4, 8, 16],
        # 'msd_p':[2, 12, 14, 16],
    }
    for i in reject.keys():
        for j in reject[i]:
            # None
            df.drop(df[np.logical_and(df['method'].str.contains(i), df['base'].astype(int)==j)].index, inplace=True)
        
    # df.drop(df[np.logical_and(df['data_size']==32, df['base'].astype(int)==16)].index, inplace=True)
    # print(df)
    return df


def g2(df, fname, lar=False):
    dsize = df['cols'].unique()
    dsizetext = ['lrg', 'med', 'sml']
    sizes = df['data_size'].unique()
    sizeVals = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    plt.rcParams.update({'font.size': 28})
    import natsort
    typeGroups = df.groupby(['data_type'])    
    for tgroup, tg in typeGroups:
        baseGroups = tg.groupby(['method'])
        for bgroup, bg in baseGroups:
            print(bgroup[0])
            # if bgroup[0]!='lsd_c':continue
            # bg['times'] = bg['times'].apply(reject_outliers,m=1)            
            bg['meantimes'] = bg['times'].apply(np.mean)            
            fig, ax = plt.subplots(figsize=(30,10))         
            order = list(bg.loc[max(bg['cols'])==bg['cols']].sort_values(by=['methodbase'], ascending=False, key=natsort.natsort_key)['methodbase'])
            bg = bg.explode('times')
            bg = bg.sort_values(by=['cols'])
            bg['times'] = bg['times'].astype(np.float32)

            bg['data_size'] = bg['data_size'].apply(lambda x: sizeVals[x])

            bg.reset_index(drop=True, inplace=True)

            bg['Method'] = bg['methodbase'].astype(str)
            bg['list items'] = bg['cols']
            # d = sns.load_dataset(bg)
            # g = sns.FacetGrid(d, col='lim',hue='Method')
            # g.map(sns.lmplot, x='list items', y='times', order=2, x_bins=100, x_estimator=np.mean, scatter=True, fit_reg=True, height=10, aspect=1.5, x_ci=None)
            g = sns.lmplot(data=bg, x='list items', y = 'times', col='lim',  order=2,hue='Method', hue_order=order, x_bins=100, x_estimator=np.mean, scatter=True,fit_reg=True, height=10, aspect=1.5,x_ci=None, facet_kws={'sharex':False, 'sharey':False})
            g.fig.suptitle(f'{bgroup[0]}')
            g.fig.axes[0].set_title(f'')
            g.fig.axes[1].set_title(f'')
            cax = plt.gca()
            legend = ax.get_legend_handles_labels()
            colours = {}
            for idx, i in enumerate(legend[0]):
                colours[legend[1][idx]] = i._color
            # for handle in bg['methodbase'].unique():
            #     sns.regplot(data=bg.loc[bg['methodbase']==handle], x='data_size', y = 'times', scatter=False,  line_kws={"ls":'--', 'color': colours[handle]}),
            # handles, labels = ax.get_legend_handles_labels()
            # print([handles[idx] for idx in order])
            # ax.legend(handles, labels, title='Method', shadow=True, loc='center left', bbox_to_anchor=(1, 0.5))
            # ax.legend(legend[0], legend[1])
            
            ticks = [x for x in bg['data_size'].unique() if (int(x)%2)!=0]
            ax.set_xticks(ticks)
            graphdir = Path('graphs') / Path(fname).stem
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            filename = f"{bgroup[0]}_length.png" if lar else f"{bgroup[0]}_length.png"
            plt.subplots_adjust(bottom=0)
            plt.savefig(graphdir / filename)
            print(graphdir / filename)
            plt.close()

                


        

if __name__ == '__main__':
    data=[]

    # g2(get_data(('/home/will/dissertation/sort_times_in_diss/lengthgraphs1e5.json')), 'lengthgraphs9')

    data1 = get_data('/home/will/dissertation/sort_times_in_diss/lengthgraphs1e6.json')
    data1['lim'] = '1,000,000'
    
    data2 = get_data('/home/will/dissertation/sort_times_in_diss/lengthgraphs1e5.json')
    data2['lim'] = '100,000'
    g2(pd.concat([data1,data2]), 'lengthgraphs13', lar=False)


    