from calendar import c
import json
import stat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import natsort
import os
pd.set_option('display.max_rows', 10)
pd.set_option('expand_frame_repr', False)
def reject_outliers(df, m=2, dropna=True):
    df = np.array(df)
    d = np.abs(df - np.median(df))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return df[s < m] if dropna else [x if (np.abs(x - np.median(df)) / (mdev or 1.)<m).any()else None for x in df ]
def stats(df):
    df.sort_values(by=['times'], inplace=True)
    print(df)
def do_graph(reject_outliers, fname, stats=True):
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
        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 36})

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

            subfigs = fig.subfigures(1, sgb.ngroups, hspace=0.1)
            subfigs = subfigs.flatten() if sgb.ngroups > 1 else [subfigs]

            for subgroup, subfig in zip(sgb.groups, subfigs):
                df3 = sgb.get_group(subgroup)
                subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                # print(df3.head(10))
                lim = np.mean(df3.loc[df3['method'] == 'timsort_n', 'times'].values[0])
                df4 = df3.copy()
                df4.loc[:,['times']] = df4['times'].apply(reject_outliers, m=3)
                df4['times'] = df4['times'].apply(lambda x: np.mean(x))
                # idxs = (list(df3[np.logical_and(True, (df4.times > lim))].index))
                # df3.loc[idxs,'times'] = 0
                if stats:
                    if group[0]!='Sorted' and group[0]!='Reverse Sorted':
                        df4['diff'] = df4['times'] - lim
                        # df4['pdiff'] = round((df4['diff'] / lim) * 100, 1)
                        df4.sort_values(by=['diff'], inplace=True)
                        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
                            results.append(df4)

    results = pd.concat(results)

    results.reset_index(inplace=True)
    # for gr, g in :
    #     print(gr)
    #     print(g)
    # print(results)
    # temp = (results.groupby(['data_type', 'cols', 'data_size','method'], as_index=False)[['times','base']].agg({'times':min, 'base':'first'})) 


        # print(len(g))
    temp = (results.groupby(['data_type', 'cols', 'data_size','method'], as_index=False).apply(get_suitable2))
    # print(temp)
    temp.reset_index(drop=True, inplace=True)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(temp.groupby(['method','base'])['method'].agg(['count']).sort_values(by=['method','count'], ascending=False))
        counts = (temp.groupby(['method','base'],as_index=False)['method'].agg(['count']).sort_values(by=['method','count'], ascending=False).groupby('method').agg('first'))
        for fi, f in counts.groupby('method'):
            if fi=='msd_c':f['base'].values[0]='10'
            if fi=='msd_p':f['base'].values[0]='6'
            if fi=='lsd_p':f['base'].values[0]='12'
            print(fi, f['base'].values[0], f['count'].values[0])
            rejects = pd.concat([results,temp]).drop_duplicates(keep=False)
            print(rejects.loc[(rejects['method'] == fi) & (rejects['base'] == (f['base'].values[0]))])
            print('')
            results.drop(results.loc[(results['method'] == fi) & (results['base'] != (f['base'].values[0]))].index, inplace=True)
    
    print(results.loc[results.groupby(['data_type', 'cols', 'data_size'], as_index=True).times.idxmin()].groupby('method')['method'].agg('count'))
    results.drop(results.loc[results['data_type'] != 'Random'].index, inplace=True)
    print(results.loc[results.groupby(['data_type', 'cols', 'data_size'], as_index=True).times.idxmin()].groupby('method')['method'].agg('count'))
    # temp2 = (results.groupby(['data_type', 'cols', 'data_size'], as_index=False))
    # for gi, g in temp2:
    #     print(gi)
    #     print(g)
    
    # for ir, i in temp:
    #     i['diff'] = ((i['times'] - min(i['times']))/min(i['times']))*100
    #     # i.drop(i.loc[i['diff'] > 100].index, inplace=True)
    #     # i.drop(i.loc[np.median(i['diff']) < i['diff']].index, inplace=True)
    #     # i.drop(i.loc[np.median(i['diff']) < i['diff']].index, inplace=True)
    #     if len(i)!=1:
    #         from scipy import stats
    #         # i['diffreject'] = reject_outliers(i['times'], m=1, dropna=False)
    #         i.drop(i.loc[(i['times'] > 2*np.min(i['times']))].index, inplace=True)
    #         i.drop(i.loc[stats.zscore(i['times']) > 1].index, inplace=True)
    #         # i.drop(i.loc[pd.isna(i['diffreject']) & (i['times'] > np.median(i['times']))].index, inplace=True)
    #         # i.drop(i.loc[i['diff'] >], axis=1, inplace=True)
    #         # i.apply(lambda x: x['diffreject'], axis=1)
    #         print(i)
    # print(temp)
    # print(temp.pivot(index=['data_type', 'data_size', 'cols'], columns=['method'], values=['base', 'times']))
    # for gr, g in results.groupby(['data_type', 'cols', 'data_size','method'], as_index=False)[['times','base']].agg({'times':min, 'base':'first'}).groupby(['data_type', 'cols', 'data_size']):
    #     print(gr) 
    #     print(g.sort_values(by='times'))
    # randvsrt(results)
    # bestbase(results)

    # groups = results.groupby(['data_type', 'cols', 'data_size'])
    # for gr, group in groups:
    #     # if gr==('Random', 1000000, 'tiny'):
    #     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified     
    #         # for gr2, group2 in group.groupby(['method']):
    #         #     if gr2[0]!='msd_c':continue
    #         #     print(group2)
    #         #     print('')
    #         print(group.loc[group.groupby(['method']).times.idxmin()].pivot(index=['data_type', 'data_size', 'cols', 'rows'], columns='method', values='base'))
    # gr = groups.agg(lower=pd.NamedAgg(column="diff", aggfunc=lambda x: sum(x<0)), diff=pd.NamedAgg(column="diff", aggfunc="mean"), perc_diff=pd.NamedAgg(column="pdiff", aggfunc="mean"))
    
    # groups = results.groupby(['method', 'base'])
    # gr = groups.agg(lower=pd.NamedAgg(column="diff", aggfunc=lambda x: sum(x<0)), diff=pd.NamedAgg(column="diff", aggfunc="mean"), perc_diff=pd.NamedAgg(column="pdiff", aggfunc="mean"))
    # groupsnons = results.drop(results[results['data_type'] == 'Nearly Sorted'].index).groupby(['method', 'base'])
    # grnons = groupsnons.agg(pdiff_no_ns=pd.NamedAgg(column="pdiff", aggfunc="mean"))
    # groupns = results[results['data_type'] == 'Nearly Sorted'].groupby(['method', 'base'])
    # grns = groupns.agg(pdiff_ns=pd.NamedAgg(column="pdiff", aggfunc="mean"))
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     gr = gr.merge(grnons, left_index=True, right_index=True).merge(grns, left_index=True, right_index=True).sort_values(by=['pdiff_no_ns'])
    #     print(gr)
    # print(grnons)
    # groups = results.groupby(['data_type', 'data_size'])
    # allprint = []
    # for group, g in groups:
    #     print(f'-----------{group[0]} - {group[1]}-----------')
    #     gr = g.groupby(['method', 'base'])
    #     gr = gr.agg(unnamed=pd.NamedAgg(column="diff", aggfunc=lambda x: sum(x<0)), diff=pd.NamedAgg(column="diff", aggfunc="mean"), avetime=pd.NamedAgg(column='times', aggfunc='mean')).sort_values(by=['avetime'])
    #     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #         print(gr)
    
    # print(df)#
    
def randvsrt(results):
    randomvsdiff = results.pivot(index=['cols','data_size','method','base'], columns='data_type', values='times').rename_axis(None, axis=1).reset_index().drop('Nearly Sorted', axis=1)
    randomvsdiff['diff'] = (randomvsdiff['Random'] - randomvsdiff['Few Unique']) / randomvsdiff['Random'] * 100
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified    
        for gr, g in randomvsdiff.groupby(['method'],as_index=False):
            print(gr[0])
            # print(g)
            # print((g.groupby(['cols'], axis=0)[['Nearly Sorted', 'Random']].apply(rejout)))
            gp = g.pivot(columns=['base'], index=['cols', 'data_size',], values='diff').reindex(natsort.natsorted(g['base'].unique()), axis=1)
            # gp = gp.rename_axis(None, axis=1).reset_index()
            # print()
            # print(gp.groupby(['cols'], axis=0)[['2','4','6','8','10','12','14','16']].agg({rejout}))

            gp =(gp.apply(reject_outliers, m=3, dropna=False, axis=1, result_type='broadcast'))

            gp['mean'] = gp.mean(axis=1, skipna=True)
            gp.loc['mean'] = gp.mean(skipna=True)
            print(gp)
            print('')
def get_suitable2(g):
    if len(g)>1:
        from sklearn.cluster import KMeans
        from scipy import stats
        kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto")
        g['group'] = kmeans.fit_predict(g[['times']])
        g.sort_values(by=['times'], inplace=True)
        # g.drop(g.loc[stats.zscore(abs(g['times'])) < 1].index, inplace=True)
        # group = (g.loc[(g['group'] == g['group'].values[0])]['times'])
        # g['std'] = g['times'] - (np.mean(group) + (2*np.std(group)))
        # g['zscore'] = 
        g.drop(g.loc[(g['group'] != g['group'].values[0]) & (abs(stats.zscore(g['times'])) > 0.5)].index, inplace=True)
        g.drop(['group'], axis=1, inplace=True)
    return g
def get_suitable(i):
    from scipy import stats
    i.drop(i.loc[(i['times'] > 2*np.min(i['times']))].index, inplace=True)
    i.drop(i.loc[stats.zscore(i['times']) > 1].index, inplace=True)
    return i
def get_unsuitable(i):
    from scipy import stats
    i.drop(i.loc[(i['times'] < 4*np.min(i['times']))].index, inplace=True)
    return i
def rejout(x):
    # if 2.42252799921762 == (np.mean(reject_outliers(x, m=2))):
    #     print(x)
    #     print(reject_outliers(x, m=2))
    print(x)
    # print(reject_outliers(y, m=2, dropna=False))
    return (reject_outliers(x, m=2))
def bestbase(results):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified    
        bestbase = (results.groupby(['data_type', 'cols', 'data_size','method'],as_index=False).agg({'times':min,'base':'first'}).pivot(index=['data_type', 'cols', 'data_size'], columns='method', values='base').rename_axis(None, axis=1).reset_index().drop('timsort_n', axis=1))
        for gr, group in bestbase.groupby(['data_type']):
            print(group.sort_values('cols', ascending=False))
            print(' ')

if __name__ == '__main__':
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/workingfinal_alwaysinsert_workingfinal_neverinsert_11.json'))
    do_graph(reject_outliers, Path('/home/will/dissertation/sort_times_in_diss/production_0.json'))
    # do_graph(reject_outliers, Path('/home/will/dissertation/sort_times/insertion_evident_0.json'))
    # for i in range(3,4):
    #     fname = Path('/home/will/dissertation/sort_times') / f'fewer_iters_tim_{i}.json'
    #     do_graph(reject_outliers, fname)