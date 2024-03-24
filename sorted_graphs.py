import json
from matplotlib import colors
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
            df2['version'] = df2['method'].str.extract(r'(?!\D*\d+)(\D+)')
            df2["version"] = df2['version'].str.strip('_')
            df2[['method', 'base']] = df2['method'].str.extract(r'(\D+)(\d+)')
            df2["method"] = df2["method"].str.replace("times.", "", regex=False).str[:-1]
            df2 = df2.dropna()
            sgb = df2.groupby(['data_size'])
            fig = plt.figure(figsize=((15*sgb.ngroups)+5, 15), constrained_layout=True)
            rows = g.rows.values[0]
            fig.suptitle(f'List length: {dsid:,}\nList count: {rows:,}\nData type: {group[0]}', fontsize='x-large')

            subfigs = fig.subfigures(1, sgb.ngroups)
            subfigs = subfigs.flatten() if sgb.ngroups > 1 else [subfigs]
            for subgroup, subfig in zip(sgb.groups, subfigs):
                df3 = sgb.get_group(subgroup)
                subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                # print(df3.head(10))
                methodgroups = df3.groupby(['method'])
                axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey=False, width_ratios=methodgroups.size())
                for idx, (key, ax) in enumerate(zip(methodgroups.groups.keys(), np.ravel([axes]))):
                    # if 'p' in key:continue
                    # print(key)
                    mdf = methodgroups.get_group(key)
                    # print(mdf)
                    mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
                    mdf = mdf.sort_values(by=['base'], key=natsort.natsort_keygen())
                    xerrors = mdf['times'].apply(np.std)
                    x = mdf['times'].apply(np.mean)
                    mdf['base'] =  mdf['base'].astype(int)
                    mdf['base'] = mdf.apply(lambda x: x['base']-0.4 if x['version']=='prod_withsorted' else x['base']+0.4, axis=1)
                    colors = {'with sorted':'C0', 'not sorted':'C1'}         
                    labels = list(colors.keys())
                    handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
                    ax.bar(mdf['base'], x, width=0.7, yerr=xerrors, color=['C0', 'C1'])
                    plt.legend(handles, labels)
                    ax.set_xlabel(key)                                      
                    # if key == list(methodgroups.groups.keys())[0]:
                    # else:
                    ax.set_ylabel('mean sort time (s)')
                    ax.tick_params(axis='y', left=False)
                    ax.spines["left"].set_visible(True)
                    # ax.set_ylabel('')
                    ax.spines["right"].set_visible(False)
                    ax.spines["top"].set_visible(False)

            graphdir = Path('graphs') / Path(fname).stem
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            gname = str(group).replace(' ', '_').strip('(,)\'')
            filename = f"{ds}_{gname}.png"
            plt.savefig(graphdir / filename)
            print(graphdir / filename)
            plt.close()

if __name__ == '__main__':
    do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/prod_withsorted_production_1.json'))