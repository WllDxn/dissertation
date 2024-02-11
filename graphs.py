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
    dsize = ['lrg', 'med', 'sml']
    dsidsint = [1000000, 100000, 10000]
    sizes = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    
    for dsid, ds in zip(dsidsint, dsize):
        with open(fname, 'r') as f:
            dataset = json.load(f)
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.drop(['files', 'read', 'key'], axis=1, errors='ignore')
        df = df[df.cols == dsid]
        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 22})

        for group, g in gb:
            fig = plt.figure(figsize=(60, 15), constrained_layout=True)
            rows = g.rows.values[0]
            fig.suptitle(f'List length: {dsid}\nList count: {rows}\nData type: {group}', fontsize='x-large')
            df2 = g.melt(id_vars=['data_type', 'data_size', 'cols', 'rows'], var_name='method', value_name='times')
            df2[['method', 'base']] = df2['method'].str.extract(r'(\D+)(\d+)')
            df2["method"] = df2["method"].str.replace("times.", "", regex=False).str[:-1]
            df2 = df2.dropna()
            sgb = df2.groupby(['data_size'])

            subfigs = fig.subfigures(1, sgb.ngroups, hspace=20)
            for subgroup, subfig in zip(sgb.groups, subfigs.flat):
                df3 = sgb.get_group(subgroup)
                subfig.suptitle(f'Limit: {subgroup} - {sizes[subgroup]}')
                methodgroups = df3.groupby(['method'])
                axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey=True)
                for key, ax in zip(methodgroups.groups.keys(), np.ravel([axes])):
                    mdf = methodgroups.get_group(key)
                    # print(mdf)
                    mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
                    mdf = mdf.sort_values(by=['base'], key=natsort.natsort_keygen())
                    xerrors = mdf['times'].apply(np.std)
                    x = mdf['times'].apply(np.mean)
                    ax.bar(mdf['base'], x, yerr=xerrors, color='C0' if key != 'tim' else 'C8')
                    ax.set_xlabel(key)
                    ax.set_ylabel('mean sort time (s)' if key == list(methodgroups.groups.keys())[0] else '')
                    ax.spines["top"].set_visible(False)
            graphdir = Path('graphs') / Path(fname).stem
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            gname = str(group).replace(' ', '_').strip('(,)\'')
            filename = f"{ds}_{gname}.jpg"
            plt.savefig(graphdir / filename)
            print(graphdir / filename)
            plt.close()

if __name__ == '__main__':
    for i in range(3,4):
        fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_tim_{i}.json'
        do_graph(reject_outliers, fname)