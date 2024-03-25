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
        'lsd_c':[2, 4, 6, 8, 16],
        'lsd_p':[2, 4, 16, 14, 8],
        'msd_c':[2, 4, 8, 16],
        'msd_p':[2, 12, 14, 16],
    }
    for i in reject.keys():
        for j in reject[i]:
            None
            # df.drop(df[np.logical_and(df['method'].str.contains(i), df['base'].astype(int)==j)].index, inplace=True)
        
    # df.drop(df[np.logical_and(df['data_size']==32, df['base'].astype(int)==16)].index, inplace=True)
    # print(df)
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
                print(bg)
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
                ticks = [x for x in bg['data_size'].unique() if (int(x)%2)!=0]
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
def g2(df, fname):
    dsize = df['cols'].unique()
    dsizetext = ['lrg', 'med', 'sml']
    sizes = df['data_size'].unique()
    sizeGroups = df.groupby(['data_type'])
    sizeVals = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    plt.rcParams.update({'font.size': 22})
    for sgroup, sg in sizeGroups:
        typeGroups = sg.groupby(['data_type'])
        for tgroup, tg in typeGroups:
            baseGroups = tg.groupby(['method'])
            for bgroup, bg in baseGroups:
                bg['times'] = bg['times'].apply(reject_outliers)            
                bg['meantimes'] = bg['times'].apply(np.mean)            
                fig, ax = plt.subplots(figsize=(30,10))      
                # sns.set_style("darkgrid", {'xtick.bottom': True, 'ytick.left': True})            
                order = list(bg.loc[max(bg['cols'])==bg['cols']].sort_values(by=['meantimes'], ascending=False)['methodbase'])
                # sns.relplot(data=bg, x='data_size', y = 'times', hue='methodbase', hue_order=order, kind='line',estimator='mean', errorbar="sd")
                # bg =  bg.loc[bg['cols'].astype(int) >= 83000]
                # bg =  bg.loc[bg['cols'].astype(int) > 65535]
                # bg =  bg.loc[bg['cols'].astype(int) <= 50000]
                # print(bg)
                # exit()
                # print(bg.loc[bg['cols']==max(bg['cols'])].sort_values(by=['meantimes'], ascending=False))
                bg = bg.explode('times')
                bg = bg.sort_values(by=['cols'])
                bg['times'] = bg['times'].astype(np.float32)
                # bg.reset_index(drop=True, inplace=True)
                # bg['times']=bg['times'].astype(float)
                # print(bg)
                mdsize = bg['data_size'].values[0]
                bg['data_size'] = bg['data_size'].apply(lambda x: sizeVals[x])
                # pv = bg.pivot(index='cols', columns='methodbase', values='times')
                # print(pv)
                # sns.relplot(data=pv, height=10, aspect=3, kind='line', palette=sns.color_palette("tab10"))
                # sns.lmplot(data=bg,y='cols', y = pv.columns, height=10, aspect=3)# scatter=False, height=10, aspect=3, x_estimator=np.mean
                # sns.regplot(data=bg, x='cols', y = 'times', scatter=False)
                # print(order)
                bg.reset_index(drop=True, inplace=True)
                # print(bg)
                
                sns.lmplot(data=bg, x='cols', y = 'times',lowess=True,hue='methodbase', hue_order=order, x_estimator=np.mean, scatter=True,fit_reg=True, height=10, aspect=2.5, x_ci=None)
                # plt.show()
                cax = plt.gca()
                legend = ax.get_legend_handles_labels()
                colours = {}
                for idx, i in enumerate(legend[0]):
                    colours[legend[1][idx]] = i._color
                # for handle in bg['methodbase'].unique():
                #     sns.regplot(data=bg.loc[bg['methodbase']==handle], x='data_size', y = 'times', scatter=False,  line_kws={"ls":'--', 'color': colours[handle]}),
                handles, labels = ax.get_legend_handles_labels()
                # print([handles[idx] for idx in order])
                # ax.legend(handles, labels, title='methodbase', shadow=True, loc='center left', bbox_to_anchor=(1, 0.5))
                # ax.legend(legend[0], legend[1])
                ticks = [x for x in bg['data_size'].unique() if (int(x)%2)!=0]
                ax.set_xticks(ticks)
                graphdir = Path('graphs') / Path(fname).stem
                os.makedirs(graphdir, exist_ok = True)
                graphdir.mkdir(parents=True, exist_ok=True)
                gname = str(tgroup).replace(' ', '_').strip('(,)\'')+'_'+str(bgroup[0])
                filename = f"{gname}.png"
                cax.set_title(f"{bg['method'].values[0]}")
                plt.savefig(graphdir / filename)
                print(graphdir / filename)
                plt.close()
                # exit()
                


        

if __name__ == '__main__':
    data=[]
    # data.append(get_data(('/home/will/dissertation/sort_times/all_insertion_final.json')))
    # gdata = pd.concat(data)
    # g_size(gdata, 'sort_comparison')
    # for i in range(21):
    #     with open(f'/home/will/dissertation/sort_times/workingfinal_{i}.json', 'r') as f:
    #         dataset = json.load(f)
    #         df = pd.json_normalize(dataset['radix_sort'])
    #         df = df.reindex(sorted(df.columns), axis=1)
    #         df = df.drop(['files', 'read', 'key'], axis=1, errors='ignore')
    #         df = df.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times').sort_values(by='cols')
    #         print(f'/home/will/dissertation/sort_times/workingfinal_{i}.json')
    #         print(df)
    #         print('------')
    # exit()
    data.append(get_data(('/home/will/dissertation/sort_times/workingfinal_test.json')))
    gdata = pd.concat(data)
    g2(gdata, 'lengthgraphs7')
