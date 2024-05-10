import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import natsort
import os
pd.set_option('display.max_rows', 10)
pd.set_option('expand_frame_repr', False)
def reject_outliers(df, m=2):
    df = np.array(df)
    d = np.abs(df - np.median(df))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return df[s < m]
def stats(df):
    df.sort_values(by=['times'], inplace=True)
    print(df)
def do_graph(reject_outliers, fname, stats=False, prune=False, sortedComp=False):
    dsize = ['lrg', 'med', 'sml']
    dsidsint = [1000000, 100000, 10000]
    sizes = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    results = []
    with open('/home/will/dissertation/sort_times_in_diss/timsort.json', 'r') as f:
        datasettim = json.load(f)
    dftim = pd.json_normalize(datasettim['radix_sort'])
    for dsid, ds in zip(dsidsint, dsize):
        with open(fname, 'r') as f:
            dataset = json.load(f)
        df = pd.concat([pd.json_normalize(dataset['radix_sort']), dftim])
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.drop(['files', 'read', 'key'], axis=1, errors='ignore')
        
        df = df[df.cols == dsid]
        if prune:
            df = df[np.logical_not(df['data_type']  != 'Nearly Sorted')]

        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 26})
        for group, g in gb:
            df0 = g.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times')
            # print(df2)
            df0[['method', 'base']] = df0['method'].str.extract(r'(\D+)(\d+)')
            if prune:
                df0.drop(df0.loc[(df0['base']=='2')].index, axis=0, inplace=True)
                df0.drop(df0.loc[(df0['base']=='14')].index, axis=0, inplace=True)
                df0.drop(df0.loc[(df0['base']=='16')].index, axis=0, inplace=True)


            df0["method"] = df0["method"].str.replace("times.", "", regex=False).str[:-1]
            for kdx, k in enumerate([['large',''],['med',''],['small',''],['tiny','']]):
                df2 = df0.dropna().copy()
                if len(k)<4:
                    df2.drop(df2.loc[(df2['data_size'] != k[0]) & (df2['data_size'] != k[1])].index, inplace=True)
                df2.drop(df2.index.difference(df2.loc[((df2['method'] == 'msd_c') & (df2['base'] == '10')) 
                | ((df2['method'] == 'msd_p') & (df2['base'] == '6'))
                | ((df2['method'] == 'lsd_c') & (df2['base'] == '10'))
                | ((df2['method'] == 'lsd_p') & (df2['base'] == '12'))
                | (df2['method'] == 'timsort_n')].index),inplace=True)           
                # print(df2)  
                sgb = df2.groupby(['data_size'])
                fig = plt.figure(figsize=((7.5*sgb.ngroups)+4, 10), constrained_layout=True)
                # pads = fig.get_constrained_layout_pads()
                rows = g.rows.values[0]
                fig.suptitle(f'List length: {dsid:,}\nData type: {group[0]}', fontsize='x-large')

                subfigs = fig.subfigures(1, sgb.ngroups, hspace=0.1)
                subfigs = subfigs.flatten() if sgb.ngroups > 1 else [subfigs]

                for subgroup, subfig in zip(sgb.groups, subfigs):
                    df3 = sgb.get_group(subgroup)
                    subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                    # print(df3.head(10))
                    lim = np.mean(df3.loc[df3['method'] == 'timsort_n', 'times'].values[0])
                    df4 = df3.copy()
                    df4['times'] = df4['times'].apply(lambda x: np.mean(x))
                    if prune:
                        df3 = df3[np.logical_not(df3['method']  == 'lsd_p')]
                    methodgroups = df3.groupby(['method'])
                    mgroup = methodgroups.size()
                    newmgroup = pd.Series()
                    for idx, i in enumerate(methodgroups.groups.keys()):
                        newmgroup[i] = len(methodgroups.get_group(i))+0.25
                        newmgroup[str(idx)] = 0.25
                        
                    # mgroup['timsort_n'] = 7.5
                    axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups*2, sharey=True)
                    for i in range(1,len(axes),2):
                        
                        # axes[i].axis('off')
                        axes[i].set_xticklabels([])
                        axes[i].set_xticks([])
                        axes[i].yaxis.set_visible(False)
                        axes[i].tick_params(axis='y', left=False)
                        axes[i].spines["left"].set_visible(False)
                        axes[i].set_ylabel('')
                        axes[i].spines["right"].set_visible(False)
                        axes[i].spines["top"].set_visible(False)
                        # axes[i].xaxis.set_visible(True)
                    axesout = [x for idx, x in enumerate(axes) if idx%2==0]
                    # subfig.get_layout_engine().set(w_pad=0, h_pad=0, hspace=0, wspace=0)
                    for idx, (key, ax) in enumerate(zip(methodgroups.groups.keys(), np.ravel([axesout]))):
                        # if not(group[0]=='Random' and subgroup=='tiny' and key=='msd_c'):continue
                        # if 'p' in key:continue
                        # print(key)
                        mdf = methodgroups.get_group(key)
                        print(mdf)
                        exit()
                        mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
                        mdf = mdf.sort_values(by=['base'], key=natsort.natsort_keygen())
                        # if 'timsort' in key:
                        #     mdf2 = mdf.copy()
                        #     mdf2['base'] = '2'
                        #     mdf2['times'] = [0]
                        #     mdf3 = mdf.copy()
                        #     mdf3['base'] = '4'
                        #     mdf3['times'] = [0]
                        #     mdf = pd.concat([mdf3, mdf, mdf2])    
                        #     mdf.reindex() 
                        xerrors = mdf['times'].apply(np.std)
                        x = mdf['times'].apply(np.mean)                        
                        wid=0.8 
                        # cllr = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5'] if not(group[0]=='Random' and subgroup=='tiny' and key=='msd_c') else ['C9' for _ in range(6)]
                        # print(mdf)

                        ax.bar(mdf['base'], x, width=wid, yerr=xerrors, color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5'] if 'timsort' not in key else 'C8')
                        if 'timsort' not in key:
                            ax.set_xlabel(key)
                            ax.tick_params(axis='x', labelsize=22 if prune else 18 if len(k)==1 else 16)
                        else:
                            for subax in subfig.axes[:-1]:                                
                                subax.axhline(y=np.mean(mdf['times'].tolist()[0]), xmin=0, xmax=1, color='C8')
                            ax.set_xlabel('tim  ', zorder=100)                      
                            ax.tick_params(axis='x', colors='white', labelsize=18)  
                                        
                        if key == list(methodgroups.groups.keys())[0]:
                            ax.set_ylabel('mean sort time (s)')
                        else:
                            ax.tick_params(axis='y', left=False)
                            ax.spines["left"].set_visible(False)
                            ax.set_ylabel('')
                        ax.spines["right"].set_visible(False)
                        ax.spines["top"].set_visible(False)
                if stats: continue
                graphdir = Path('graphs') / Path(fname).stem / Path('nopig') if prune else Path('graphs') / Path('winners') / Path(fname).stem 
                os.makedirs(graphdir, exist_ok = True)
                graphdir.mkdir(parents=True, exist_ok=True)
                gname = str(group).replace(' ', '_').strip('(,)\'')
                filename = f"{ds}_{gname}_nolp_{kdx}.png" if prune else f"{ds}_{gname}_{kdx}.png"
                fig.set_constrained_layout_pads(w_pad=0, h_pad=0, hspace=0, wspace=0)
                plt.savefig(graphdir / filename, bbox_inches='tight')
                print(graphdir / filename)
                plt.close()

    
    # print(df)

if __name__ == '__main__':
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/workingfinal_alwaysinsert_workingfinal_neverinsert_11.json'))
    do_graph(reject_outliers, Path('/home/will/dissertation/sort_times_in_diss/production_0.json'))
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/insertion_evident_0.json'))
    # for i in range(3,4):
    #     fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_tim_{i}.json'
    #     do_graph(reject_outliers, fname)