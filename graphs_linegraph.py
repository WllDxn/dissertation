import json
from turtle import title
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


def get_data(fname, lar=False):
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
    df = df.dropna()
    return df

def reject(df, lar=True):
    reject = {
        'lsd_c':[2,4,6,14],
        'lsd_p':[2,4,6,8],
        'msd_c':[2,4,6,14,16],
        'msd_p':[2,4,6,12,14,16],
    } if lar else {
        'lsd_c':[],
        'lsd_p':[],
        'msd_c':[],
        'msd_p':[],
    }
    for i in reject.keys():
        for j in reject[i]:
            # None
            df.drop(df[np.logical_and(df['method'].str.contains(i), df['base'].astype(int)==j)].index, inplace=True)
    return df
import colorcet as cc
def g2(df, fname):
    dsize = df['cols'].unique()
    dsizetext = ['lrg', 'med', 'sml']
    sizes = df['data_size'].unique()
    sizeVals = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    plt.rcParams.update({'font.size': 30})
    for lar in [True]:
        colrs = {}
        pal = sns.color_palette( n_colors=len(df['base'].unique()))
        for i, base in enumerate(sorted(list(df['base'].unique()), reverse=True)):
            curr = pal[-i]
                # print(base)
            for method in list(df['method'].unique()):            
                colrs[f'{method}_{base}'] = curr
        df = reject(df, lar)

        typeGroups = df.groupby(['data_type'])
        for tgroup, tg in typeGroups:
            baseGroups = tg.groupby(['method'])
            for bgroup, bg in baseGroups:
                # bg['times'] = bg['times'].apply(reject_outliers)            
                bg['meantimes'] = bg['times'].apply(np.mean)   
                bg = bg.sort_values(by=['meantimes'], ascending=True)
                fig, ax = plt.subplots(figsize=(30,10))      
                # sns.set_style("darkgrid", {'xtick.bottom': True, 'ytick.left': True})  
                # sns.relplot(data=bg, x='data_size', y = 'times', hue='methodbase', hue_order=order, kind='line',estimator='mean', errorbar="sd")
                bg = bg.explode('times')
                bg.reset_index(drop=True, inplace=True)
                bg['times']=bg['times'].astype(float)
                bg.drop(bg[bg['times']==0].index, inplace=True)
                bg.sort_values(by=['methodbase'], key=natsort.natsort_keygen(), inplace=True)
                bg['Integer Size'] = bg['data_size']
                bg['Method'] = bg['methodbase']
                order = list(bg.loc[max(bg['data_size'])==bg['data_size']]['methodbase'].drop_duplicates().sort_values(ascending=False, key=natsort.natsort_key))
                g = sns.lmplot(data=bg, x='Integer Size', y = 'times', hue='Method', hue_order=order, palette=colrs, scatter=True, height=10, aspect=2.5, lowess=True, x_ci=None,x_estimator=np.mean, facet_kws={'sharex':False, 'sharey':False})
                g.fig.suptitle(f'{bgroup[0]}')
                
                # colours = {}
                # for idx, i in enumerate(legend[0]):
                #     colours[legend[1][idx]] = i._color
                # for handle in bg['methodbase'].unique():
                #     sns.regplot(data=bg.loc[bg['methodbase']==handle], x='data_size', y = 'times', scatter=False,  line_kws={"ls":'--', 'color': colours[handle]}),
                handles, labels = ax.get_legend_handles_labels()
                # print([handles[idx] for idx in order])
                ax.legend(handles, labels, title='methodbase', shadow=True, loc='center left', bbox_to_anchor=(1, 0.5))
                # ax.legend(legend[0], legend[1])
                ticks = [x for x in bg['data_size'].unique() if (int(x)%2)!=0]
                ax.set_xticks(ticks)
                graphdir = Path('graphs') / Path(fname).stem
                os.makedirs(graphdir, exist_ok = True)
                graphdir.mkdir(parents=True, exist_ok=True)
                print(str())
                filename = f"{bgroup[0]}_base.png" if lar else f"{bgroup[0]}_a.png"
                plt.savefig(graphdir / filename, dpi=100)
                print(graphdir / filename)
                plt.close()
                


        

if __name__ == '__main__':
        data=[]
        # data.append(get_data(('/home/will/dissertation/sort_times/all_insertion_final.json')))
        # gdata = pd.concat(data)
        # g_size(gdata, 'sort_comparison')
        gdata = None
        for i in range(6,7):
            data.append(get_data((f'/home/will/dissertation/sort_times/workingfinal_2{str(i)}.json')))
            print(f'sort_comparison_bits{str(i+1)}', f'/home/will/dissertation/sort_times/workingfinal_2{str(i)}.json')
        
        g2(pd.concat(data), f'basegraphs2')
        # g2(get_data(f'/home/will/dissertation/sort_times_in_diss/workingfinal_27.json'), f'basegraphs2')
    # data.append(get_data(('/home/will/dissertation/sort_times/workingfinal_22.json')))
