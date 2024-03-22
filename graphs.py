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

def do_graph(reject_outliers, fname):
    # plt.rcParams["axes.axisbelow"] = False
    dsize = ['lrg', 'med', 'sml']
    dsidsint = [1000000, 100000, 10000]
    sizes = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    
    for dsid, ds in zip(dsidsint, dsize):
        with open(fname, 'r') as f:
            dataset = json.load(f)
        df = pd.json_normalize(dataset['radix_sort'])
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.drop(['files', 'read', 'key'], axis=1, errors='ignore')
        df = df[df.cols == dsid]
        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 22})

        for group, g in gb:
            df2 = g.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times')
            # print(df2)
            df2[['method', 'base']] = df2['method'].str.extract(r'(\D+)(\d+)')
            df2["method"] = df2["method"].str.replace("times.", "", regex=False).str[:-1]
            df2 = df2.dropna()
            sgb = df2.groupby(['data_size'])
            fig = plt.figure(figsize=((15*sgb.ngroups)+10, 15), constrained_layout=True)
            # pads = fig.get_constrained_layout_pads()
            rows = g.rows.values[0]
            fig.suptitle(f'List length: {dsid:,}\nList count: {rows:,}\nData type: {group[0]}', fontsize='x-large')

            subfigs = fig.subfigures(1, sgb.ngroups, wspace=0)
            subfigs = subfigs.flatten() if sgb.ngroups > 1 else [subfigs]

            for subgroup, subfig in zip(sgb.groups, subfigs):
                df3 = sgb.get_group(subgroup)
                subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                methodgroups = df3.groupby(['method'])
                axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey=True, width_ratios=methodgroups.size()+0.1)
                subfig.get_layout_engine().set(w_pad=0, h_pad=0, hspace=0, wspace=0)
                for idx, (key, ax) in enumerate(zip(methodgroups.groups.keys(), np.ravel([axes]))):
                    # if 'p' in key:continue
                    # print(key)
                    mdf = methodgroups.get_group(key)
                    # print(mdf)
                    mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
                    mdf = mdf.sort_values(by=['base'], key=natsort.natsort_keygen())
                    xerrors = mdf['times'].apply(np.std)
                    x = mdf['times'].apply(np.mean)
                    ax.bar(mdf['base'], x, width=0.8, yerr=xerrors, color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5']if 'timsort' not in key else ['C8'])
                    if 'timsort' not in key:
                        ax.set_xlabel(key)
                    else:
                        for subax in subfig.axes:
                            subax.axhline(y=np.mean(mdf['times'].tolist()[0]), xmin=0, xmax=1, color='C8')
                        ax.set_xlabel('tim', zorder=100)   
                        # ax.get_xlabel().set_zorder(1000)                     
                        ax.tick_params(axis='x', colors='white')  
                                      
                    if key == list(methodgroups.groups.keys())[0]:
                        ax.set_ylabel('mean sort time (s)')
                    else:
                        ax.tick_params(axis='y', left=False)
                        ax.spines["left"].set_visible(False)
                        ax.set_ylabel('')
                    ax.spines["right"].set_visible(False)
                    ax.spines["top"].set_visible(False)
            graphdir = Path('graphs') / Path(fname).stem
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            gname = str(group).replace(' ', '_').strip('(,)\'')
            filename = f"{ds}_{gname}.png"
            fig.set_constrained_layout_pads(w_pad=0, h_pad=0, hspace=0, wspace=0)
            plt.savefig(graphdir / filename, bbox_inches='tight')
            print(graphdir / filename)
            plt.close()

if __name__ == '__main__':
    do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/production_0.json'))
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/workingfinal_0.json'))
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/insertion_evident_0.json'))
    # for i in range(3,4):
    #     fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_tim_{i}.json'
    #     do_graph(reject_outliers, fname)