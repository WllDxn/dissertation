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
def do_graph(reject_outliers, fname, stats=False):
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
        # df = df[df.data_type == 'Nearly Sorted']
        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 36})

        for group, g in gb:
            df2 = g.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times')
            # print(df2)
            df2[['method', 'base']] = df2['method'].str.extract(r'(\D+)(\d+)')
            df2["method"] = df2["method"].str.replace("times.", "", regex=False).str[:-1]
            df2['base'] = df2['base'].astype(int)
            df2 = df2[((df2['base'] != 2) & (df2['base'] < 14))]
            # print(df2)
            df2['base'] = df2['base'].astype(str)
            df2 = df2.dropna()
            sgb = df2.groupby(['data_size'])
            fig = plt.figure(figsize=((15*sgb.ngroups)+10, 15), constrained_layout=True)
            # pads = fig.get_constrained_layout_pads()
            rows = g.rows.values[0]
            fig.suptitle(f'List length: {dsid:,}\nList count: {rows:,}\nData type: {group[0]}', fontsize='x-large')

            subfigs = fig.subfigures(1, sgb.ngroups, hspace=0.1)
            subfigs = subfigs.flatten() if sgb.ngroups > 1 else [subfigs]

            for subgroup, subfig in zip(sgb.groups, subfigs):
                df3 = sgb.get_group(subgroup)
                subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                # print(df3.head(10))
                lim = np.mean(df3.loc[df3['method'] == 'timsort_n', 'times'].values[0])
                df4 = df3.copy()
                df4['times'] = df4['times'].apply(lambda x: np.mean(x))
                # idxs = (list(df3[np.logical_and(True, (df4.times > lim))].index))
                # df3.loc[idxs,'times'] = 0
                if stats:
                    if group[0]!='Sorted' and group[0]!='Reverse Sorted':
                        df4['diff'] = df4['times'] - lim
                        df4['pdiff'] = round((df4['diff'] / lim) * 100, 1)
                        df4.sort_values(by=['diff'], inplace=True)
                        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
                            from math import log
                            # print(f'{dsid:,}  -  {group[0]}  -  {sizes[str(subgroup)]:,} / {int(log(sizes[str(subgroup)], 2))}')
                            # print(df4[['method', 'base','times', 'diff', 'pdiff']])
                            # print('\n')
                            results.append(df4)
                    continue
                #     stats(df4)
                # continue
                # df3 = df3.drop(df3[np.logical_and(True, (df4.times > lim))].index) * 5
                # print(df4.columns)
                # df4 = df4.drop(df4[np.logical_and(True, (df4.method != 'msd_p'))].index)

                # df4 = df4.pivot(index=['data_type', 'data_size', 'cols', 'rows'], columns=['method', 'base'], values='times')
                # df4 = df4.reindex(df4['Value'].sort_values(by=2012, ascending=False).index)
                df3 = df3[np.logical_not(df3['method']  == 'lsd_p')]
                methodgroups = df3.groupby(['method'])
                mgroup = methodgroups.size()
                mgroup['timsort_n'] = 3.5
                axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey=True, width_ratios=mgroup)
                # subfig.get_layout_engine().set(w_pad=0, h_pad=0, hspace=0, wspace=0)
                for idx, (key, ax) in enumerate(zip(methodgroups.groups.keys(), np.ravel([axes]))):
                    # if not(group[0]=='Random' and subgroup=='tiny' and key=='msd_c'):continue
                    # if 'p' in key:continue
                    # print(key)
                    mdf = methodgroups.get_group(key)
                    # print(mdf)
                    mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
                    mdf = mdf.sort_values(by=['base'], key=natsort.natsort_keygen())
                    if 'timsort' in key:
                        mdf2 = mdf.copy()
                        mdf2['base'] = '2'
                        mdf2['times'] = [0]
                        mdf3 = mdf.copy()
                        mdf3['base'] = '4'
                        mdf3['times'] = [0]
                        mdf = pd.concat([mdf3, mdf, mdf2])    
                        mdf.reindex() 
                    xerrors = mdf['times'].apply(np.std)
                    x = mdf['times'].apply(np.mean)
                    
                    wid=0.8 if 'timsort' not in key else [0, 0.6, 0]
                    # cllr = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5'] if not(group[0]=='Random' and subgroup=='tiny' and key=='msd_c') else ['C9' for _ in range(6)]
                    ax.bar(mdf['base'], x, width=wid, yerr=xerrors, color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5'] if 'timsort' not in key else ['white', 'C8', 'white'])
                    if 'timsort' not in key:
                        ax.set_xlabel(key)
                        ax.tick_params(axis='x', labelsize=24)
                    else:
                        for subax in subfig.axes:
                            subax.axhline(y=np.mean(mdf['times'].tolist()[1]), xmin=0, xmax=1, color='C8')
                        ax.set_xlabel('tim', zorder=100)                      
                        ax.tick_params(axis='x', colors='white', labelsize=18)  

                        # print(mdf)
                                      
                    if key == list(methodgroups.groups.keys())[0]:
                        ax.set_ylabel('mean sort time (s)')
                    else:
                        ax.tick_params(axis='y', left=False)
                        ax.spines["left"].set_visible(False)
                        ax.set_ylabel('')
                    ax.spines["right"].set_visible(False)
                    ax.spines["top"].set_visible(False)
            if stats: continue
        
            graphdir = Path('graphs') /     Path.joinpath(Path(fname),Path('nopig')).stem
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            gname = str(group).replace(' ', '_').strip('(,)\'')
            filename = f"{ds}_{gname}.png"
            fig.set_constrained_layout_pads(w_pad=0, h_pad=0, hspace=0, wspace=0)
            plt.savefig(graphdir / filename, bbox_inches='tight')
            print(graphdir / filename)
            plt.close()


if __name__ == '__main__':
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/workingfinal_alwaysinsert_workingfinal_neverinsert_11.json'))
    do_graph(reject_outliers, Path('/home/will/dissertation/sort_times_in_diss/production_0.json'))
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/insertion_evident_0.json'))
    # for i in range(3,4):
    #     fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_tim_{i}.json'
    #     do_graph(reject_outliers, fname)