import json
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
    return df


def g(df, fname):
    dsize = df['cols'].unique()
    dsizetext = ['lrg', 'med', 'sml']
    sizes = df['data_size'].unique()
    sizeGroups = df.groupby(['cols'])
    sizeVals = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    plt.rcParams.update({'font.size': 22})
    for sgroup, sg in sizeGroups:
        typeGroups = sg.groupby(['data_type'])
        for tgroup, tg in typeGroups:
            baseGroups = tg.groupby(['method'])
            for bgroup, bg in baseGroups:
                bg['times'] = bg['times'].apply(np.mean)            
                fig, ax = plt.subplots(figsize=(30,10))      
                # sns.set_style("darkgrid", {'xtick.bottom': True, 'ytick.left': True})            
                order = list(bg.loc[max(bg['data_size'])==bg['data_size']].sort_values(by=['times'], ascending=False)['methodbase'])
                # sns.relplot(data=bg, x='data_size', y = 'times', hue='methodbase', hue_order=order, kind='line',estimator='mean', errorbar="sd")
                sns.lineplot(data=bg, x='data_size', y = 'times', hue='methodbase', hue_order=order, estimator='mean', errorbar='pi')
                legend = ax.get_legend_handles_labels()
                colours = {}
                for idx, i in enumerate(legend[0]):
                    colours[legend[1][idx]] = i._color
                # for handle in bg['methodbase'].unique():
                #     sns.regplot(data=bg.loc[bg['methodbase']==handle], x='data_size', y = 'times', scatter=False,  line_kws={"ls":'--', 'color': colours[handle]}),
                handles, labels = ax.get_legend_handles_labels()
                # print([handles[idx] for idx in order])
                ax.legend(handles, labels, title='methodbase', shadow=True, loc='center left', bbox_to_anchor=(1, 0.5))
                # ax.legend(legend[0], legend[1])
                ticks = [x for x in bg['data_size'].unique() if (int(x)%2)==0]
                ax.set_xticks(ticks)
                graphdir = Path('graphs') / Path(fname).stem
                os.makedirs(graphdir, exist_ok = True)
                graphdir.mkdir(parents=True, exist_ok=True)
                gname = str(tgroup).replace(' ', '_').strip('(,)\'')+'_'+str(bgroup[0])
                ds = str(sgroup)
                for size, text in zip(reversed(sorted(dsize)), dsizetext):
                    if size == sgroup:
                        ds = text
                filename = f"{ds}_{gname}.jpg"
                plt.savefig(graphdir / filename)
                print(graphdir / filename)
                plt.close()
                
def g_size(df, fname):
    dsize = df['cols'].unique()
    dsizetext = ['lrg', 'med', 'sml']
    sizes = df['data_size'].unique()
    sizeVals = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    plt.rcParams.update({'font.size': 22})
    # typeGroups = df.groupby(['data_type'])
    sizeGroups = df.groupby(['data_size'])
    for sgroup, sg in sizeGroups:
        typeGroups = sg.groupby(['data_type'])
        for tgroup, tg in typeGroups:
            baseGroups = tg.groupby(['method'])
            for bgroup, bg in baseGroups:
                bg['times'] = bg['times'].apply(np.mean)    
                fig, ax = plt.subplots(figsize=(50,10))      
                sns.set_style("darkgrid", {'xtick.bottom': True, 'ytick.left': True})            
                order = list(bg.loc[max(bg['cols'])==bg['cols']].sort_values(by=['times'], ascending=False)['methodbase'])
                # print(bg)
                sns.lineplot(data=bg, x='cols', y = 'times', hue='methodbase', hue_order=order, estimator='mean')
                legend = ax.get_legend_handles_labels
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles, labels, title='methodbase', shadow=True, loc='center left', bbox_to_anchor=(1, 0.5))
                graphdir = Path('graphs') / Path(fname).stem
                os.makedirs(graphdir, exist_ok = True)
                graphdir.mkdir(parents=True, exist_ok=True)
                gname = str(tgroup).replace(' ', '_').strip('(,)\'')+'_'+str(bgroup[0])
                filename = f"{sgroup[0]}_{gname}.jpg"
                plt.savefig(graphdir / filename)
                print(graphdir / filename)
                plt.close()
                
def g_sorted_nosort(df, fname):
    dsize = df['cols'].unique()
    dsizetext = ['lrg', 'med', 'sml']
    sizes = df['data_size'].unique()
    sizeGroups = df.groupby(['cols'])
    sizeVals = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    plt.rcParams.update({'font.size': 22})
    for sgroup, sg in sizeGroups:
        typeGroups = sg.groupby(['data_type'])
        for tgroup, tg in typeGroups:
            baseGroups = tg.groupby(['methodbase'])
            for bgroup, bg in baseGroups:
                bg['times'] = bg['times'].apply(np.mean)
                fig, ax = plt.subplots(figsize=(40,10))      
                sns.set_style("whitegrid", {'xtick.bottom': True, 'ytick.left': True})            
                sns.lineplot(data=bg, x='data_size', y = 'times', hue='implementation',  palette=['g', 'r'], estimator='mean', errorbar='se')
                for handle in bg['implementation'].unique():
                    sns.regplot(data=bg.loc[bg['implementation']==handle], x='data_size', y = 'times', scatter=False,  line_kws={"ls":'--'}, label=handle+'-regression')
                legend = ax.get_legend_handles_labels()
                legend[0].sort(key=lambda x: x.get_label())
                legend[1].sort()
                ax.legend(legend[0], legend[1], title='Implementation')
                ax.set_xticks(bg['data_size'].unique())
                graphdir = Path('graphs') / Path(fname).stem
                os.makedirs(graphdir, exist_ok = True)
                graphdir.mkdir(parents=True, exist_ok=True)
                gname = str(tgroup).replace(' ', '_').strip('(,)\'')+'_'+str(bgroup[0])
                ds = str(sgroup)
                for size, text in zip(reversed(sorted(dsize)), dsizetext):
                    if size == sgroup:
                        ds = text
                filename = f"{ds}_{gname}2.jpg"
                plt.savefig(graphdir / filename)
                print(graphdir / filename)
                plt.close()

        

if __name__ == '__main__':
    data=[]
    # data.append(get_data(('/home/will/dissertation/sort_times/all_insertion_final.json')))
    # gdata = pd.concat(data)
    # g_size(gdata, 'sort_comparison')
    
    data.append(get_data(('/home/will/dissertation/sort_times/all_bits.json')))
    gdata = pd.concat(data)
    g(gdata, 'sort_comparison_bits')
