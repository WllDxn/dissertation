import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_rows', 10)

def reject_outliers(df, m=2):
    d = np.abs(df - np.median(df))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return df[s < m]

if __name__ == '__main__':
    dsize = ['lrg', 'med', 'sml']
    dsidsint = [1000000, 100000, 10000]
    sizes = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}

    for dsid, ds in enumerate(dsize):
        with open('switchtest.json', 'r') as f:
            dataset = json.load(f)
        df = pd.json_normalize(dataset['radix_sort'])
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.drop(['files', 'read', 'key'], axis=1, errors='ignore')
        df.drop(df[df.cols != dsidsint[dsid]].index, inplace=True)
        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 22})

        for group in gb.groups:
            fig = plt.figure(figsize=(60, 15), constrained_layout=True)
            rows = gb.get_group(group).rows.values[0]
            fig.suptitle(f'List length: {dsidsint[dsid]}\nList count: {rows}\nData type: {group}', fontsize='x-large')

            df2 = gb.get_group(group).melt(id_vars=['data_type', 'data_size'], var_name='method', value_name='times')
            df2[['method', 'base']] = df2['method'].str.split('_base', expand=True)
            df2["method"] = df2["method"].str.replace("times.", "").str.replace("_sort", "")
            df2 = df2.dropna()
            sgb = df2.groupby(['data_size'])

            if sgb.ngroups < 1:
                continue

            subfigs = fig.subfigures(1, sgb.ngroups, hspace=20)
            for subgroup, subfig in zip(sgb.groups, subfigs.flat):
                df3 = sgb.get_group(subgroup)
                subfig.suptitle(f'Limit: {subgroup} - {sizes[subgroup]}')
                methodgroups = df3.groupby(['method'])

                axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey=True)
                for key, ax in zip(methodgroups.groups.keys(), axes.flatten()):
                    mdf = methodgroups.get_group(key)
                    mdf['times'] = mdf['times'].apply(reject_outliers)
                    mdf.sort_values(by=['base'], key=lambda x: x.str.len(), inplace=True)

                    xerrors = mdf['times'].apply(np.std)
                    x = mdf['times'].apply(np.mean)
                    ax.bar(mdf['base'], x, yerr=xerrors, color='C0' if key != 'tim' else 'C8')
                    ax.set_xlabel(key)
                    ax.set_ylabel('mean sort time (s)' if key == methodgroups.groups.keys()[0] else '')
                    ax.spines["top"].set_visible(False)

            filename = f"{ds}{group.replace(' ', '_')}.jpg"
            url = f"graphs/switch/{filename}"
            plt.savefig(url)
            print(filename)
