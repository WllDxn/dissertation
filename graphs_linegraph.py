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
    df = df.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times')
    df['implementation'] = df['method'].str.extract(r'([^\_]+$)')
    df['methodbase'] = df['method'].str.replace("times.", "", regex=False)
    df[['method', 'base']] = df['method'].str.extract(r'(\D+)(\d+)')
    df["method"] = df["method"].str.replace("times.", "", regex=False) + df['implementation']
    # df['method'] += 'nosort' if ('nosort') in fname else 'sort'
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
            tg['times'] = tg['times'].apply(np.mean)
            plt.figure(figsize=(40,10))
            sns.set_style("whitegrid", {'xtick.bottom': True, 'ytick.left': True})
            
            g = sns.lineplot(data=tg, x='data_size', y = 'times', hue='methodbase')
            print(max(tg['data_size'].unique()))
            g.set_xticks(tg['data_size'].unique())
            graphdir = Path('graphs') / Path(fname).stem
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            gname = str(tgroup).replace(' ', '_').strip('(,)\'')
            ds = str(sgroup)
            for size, text in zip(reversed(sorted(dsize)), dsizetext):
                if size == sgroup:
                    ds = text
            filename = f"{ds}_{gname}.jpg"
            plt.savefig(graphdir / filename)
            print(graphdir / filename)
            return
            # fig = plt.figure(figsize=((15*dataSizeGroups.ngroups)+5, 15), constrained_layout=True)
            
            
            
            
            
            
            
            
            
            
            
            
            # fig = plt.figure(figsize=((15*dataSizeGroups.ngroups)+5, 15), constrained_layout=True)
            # fig.get_layout_engine().set(w_pad=0, h_pad=0, hspace=0,wspace=0)
            # rows = tg.rows.values[0]
            # # sregex = re.compile('[^a-zA-Z]')
            # sgroupstr = int(re.sub(r"[^\d]+","", str(sgroup)))
            # sgroupstr = f'{sgroupstr:,}'
            # rowsstr = re.sub(r"[^\d]+","", str(rows))
            # tgroupstr = re.sub(r"[^a-zA-Z ]+","", str(tgroup))
            # fig.suptitle(f'List length: {sgroupstr}\nList count: {rowsstr}\nData type: {tgroupstr}', fontsize='x-large')
            # subfigs = fig.subfigures(1, dataSizeGroups.ngroups, hspace=20)
            # subfigs = subfigs.flatten() if dataSizeGroups.ngroups > 1 else [subfigs]
            # for subgroup, subfig in zip(dataSizeGroups.groups, subfigs):    
            #     df3 = dataSizeGroups.get_group(subgroup)

            #     limitsry = f'{sizeVals[subgroup]: }'
            #     subfig.suptitle(f'Limit: {subgroup} - {limitsry}')
            #     methodgroups = df3.groupby(['method'])
            #     axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey='all', width_ratios=methodgroups.size())
            #     for (key, ax) in zip(methodgroups.groups.keys(), np.ravel([axes])):
            #         mdf = methodgroups.get_group(key)
            #         mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
            #         mdf = mdf.sort_values(by=['base'], key=natsort.natsort_keygen())
            #         xerrors = mdf['times'].apply(np.std)
            #         mdf['xerrors'] = mdf['times'].apply(np.std)
            #         x = mdf['times'].apply(np.mean)
            #         mdf['times'] = mdf['times'].apply(np.mean)
            #         mdf['xerrors'] = mdf['xerrors'].where(mdf['xerrors'] < mdf['times'], mdf['times'])
                    
            #         ax.bar(mdf['base'], mdf['times'], width=0.8, yerr=mdf['xerrors'], color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5']if 'timsort' not in key else ['C8'])
            #         if 'timsort' not in key:
            #             ax.set_xlabel(key)
            #         else:
            #             ax.set_xlabel('timsort')                        
            #             ax.tick_params(axis='x', colors='white')  
                                      
            #         if key == list(methodgroups.groups.keys())[0]:
            #             ax.set_ylabel('mean sort time (s)')
            #         else:
            #             ax.tick_params(axis='y', left=False)
            #             ax.spines["left"].set_visible(False)
            #             ax.set_ylabel('')
            #         ax.spines["right"].set_visible(False)
            #         ax.spines["top"].set_visible(False)
                    
            # graphdir = Path('graphs') / Path(fname).stem
            # os.makedirs(graphdir, exist_ok = True)
            # graphdir.mkdir(parents=True, exist_ok=True)
            # gname = str(tgroup).replace(' ', '_').strip('(,)\'')
            # ds = str(sgroup)
            # for size, text in zip(reversed(sorted(dsize)), dsizetext):
            #     if size == sgroup:
            #         ds = text
            # filename = f"{ds}_{gname}.jpg"
            # plt.savefig(graphdir / filename)
            # print(graphdir / filename)
            # plt.close()
        

if __name__ == '__main__':
    data=[]
    data.append(get_data(('/home/will/dissertation/sort_times/final_5.json')))
    # data.append(get_data(('/home/will/dissertation/sort_times/workingfinal_0.json')))
    # data.append(get_data(('/home/will/dissertation/sort_times/insertion_evident_0.json')))
    # for i in [12]:
    #     fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_insertion_evident_timsort_{i}.json'
    #     data.append(get_data(fname))
    gdata = pd.concat(data)
    print(gdata)
    g(gdata, 'final')
    # get_data(Path('/home/will/dissertation/sort_times/fewer_iters_insertion_evident_timsort_11.json'))
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/fewer_iters_insertion_evident_timsort_11.json'))
    # for i in range(3,4):
    #     fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_tim_{i}.json'
    #     do_graph(reject_outliers, fname)