from ast import Name
from calendar import c
import json
import stat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import natsort
import os

from pyparsing import col
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
    bestofbest(results)
    # normalr(results)
    # bestmethod(results)


def bestofbest(results):
    # grafresults(results.drop(results.loc[results['data_type'] == 'Few Unique'].index))
    grafresults(results)
    print('-------------------')
    grafresults(results.drop(results.loc[results['data_type'] != 'Random'].index))
    print('-------------------')
    grafresults(results.drop(results.loc[results['data_type'] != 'Nearly Sorted'].index))
    # results.drop(results.loc[(results['method'] != 'timsort_n') & (results['method'] != 'lsd_p')].index, inplace=True)
    
def grafresults(results):
    results.drop(results.index.difference(results.loc[((results['method'] == 'msd_c') & (results['base'] == '10')) 
                            | ((results['method'] == 'msd_p') & (results['base'] == '6'))
                            | ((results['method'] == 'lsd_c') & (results['base'] == '10'))
                            | ((results['method'] == 'lsd_p') & (results['base'] == '12'))
                            | (results['method'] == 'timsort_n')].index),inplace=True)
    
        
    results['times'] = results.groupby(['data_type', 'cols', 'data_size'])[['times']].transform(lambda g: (g - np.mean(g)) / np.std(g))
    results['rank'] = (results.groupby(['data_type', 'cols', 'data_size']).agg(rank=pd.NamedAgg(column='times', aggfunc='rank'))['rank'].astype(int))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        # print(results.loc[results['method']=='timsort_n'])
        for cat in [ 'data_type','cols', 'data_size', '']:
            print(cat)
            r = (results.groupby(['method',cat] if cat!='' else ['method']).agg(
                rank=pd.NamedAgg(column='rank', aggfunc='mean'),
                ranksum=pd.NamedAgg(column='rank', aggfunc='sum'),
                times=pd.NamedAgg(column='times', aggfunc='mean')
            ).sort_values(by=['method'], ascending=False).reset_index())
            r['rank'] = np.round(r['rank'],2)
            r['times'] = np.round(r['times'],2)
            if cat!='':
                r=r.pivot(index='method', columns=[cat], values=['rank', 'times'])
                r.columns = r.columns.swaplevel(0,1)
                r = r.sort_index(axis=1)
                print(r.to_latex(index=True,

                  formatters={"name": str.upper},

                  float_format="{:.4}".format,))  
                # print(r)
            else:
                print(r[['method','rank','times']])
        # print(results.groupby(['method']).agg(
        #     rank=pd.NamedAgg(column='rank', aggfunc='mean'),
        #     ranksum=pd.NamedAgg(column='rank', aggfunc='sum'),
        #     times=pd.NamedAgg(column='times', aggfunc='mean')
        # ).sort_values(by=['ranksum'], ascending=False))
        # for gi, g in results.groupby(['data_type', 'cols', 'data_size']):
        #     print(gi)
        #     print(g)
        #     print('')
        # countdf.reset_index(inplace=True)
        # print(countdf)
def normalr(results, drop=True):
    # print(results)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        if drop:
            results.drop(results.loc[results['method'] == 'timsort_n'].index, inplace=True)
        from scipy import stats
        # results = (results.groupby(['data_type', 'cols', 'data_size','method'], as_index=False).apply(lambda g:  g.drop(g.loc[((stats.zscore(g['times'])) > 1)].index)))
        # results['times'] = results.groupby(['data_type', 'cols', 'data_size'])[['times']].transform(lambda g: (g - np.mean(g)) / np.std(g))
        results['times'] = results.groupby(['data_type', 'cols', 'data_size','method'])[['times']].transform(lambda g: (g - np.mean(g)) / np.std(g))
        countdf = results.groupby(['method', 'base']).agg(
            times=pd.NamedAgg(column="times", aggfunc="mean"),                   
            ).reset_index().sort_values(by=['times'])
        # print(countdf)
        countdf['rank'] = countdf.groupby(['method'])[['times']].transform('rank','first',ascending=True).astype(int)
        countdf.sort_values(['method','rank'], inplace=True)
        countdf = countdf.pivot(index='rank', columns='method', values=['base','times'])
        countdf.columns = countdf.columns.swaplevel(0,1)
        countdf = countdf.sort_index(axis=1)
        # countdf = countdf.pivot(columns='method', values=['base', 'count'])
        countdf.rename(columns={'lsd_c':'lsd c','lsd_p':'lsd p','msd_c':'msd c','msd_p':'msd p'}, inplace=True)
        co = [(x,'times') for x in ['lsd c','lsd p','msd c','msd p']]
        countdf[co] = countdf[co].astype(float)
        countdf[co] = countdf[co].round(3) 
        print(countdf)
                
        print(countdf.to_latex(index=True,

                  formatters={"name": str.upper},

                  float_format="{:.4}".format,))  
        results.sort_values(by=['times'], inplace=True)
        results.drop(results.loc[(results['base'] != '10')& (results['base'] != '12')].index, inplace=True)
        t2 = (results.groupby(['data_type','data_size','cols','method'],as_index=True).agg(
            first=pd.NamedAgg(column="base", aggfunc="first"),
            max=pd.NamedAgg(column="times", aggfunc='max'),
            min=pd.NamedAgg(column="times", aggfunc='min'),            
              ))
        t2['diff'] = abs(abs(t2['max']) - abs(t2['min']))
        t2.drop(columns=['min','max'],inplace=True)
        print(t2)
        t2.sort_values(by=['data_type','data_size','cols'], inplace=True)
        # # print(t2.loc[(t2['first']=='8') & (t2['method']=='lsd_c')])
        # print(t2.loc[(t2['method']=='lsd_c')].sort_values(by=['first','data_type','cols', 'data_size'],ascending=False))
        print(t2.groupby(['method','first'],as_index=False).agg(
            count=pd.NamedAgg(column="first", aggfunc="count"),
            diff=pd.NamedAgg(column="diff", aggfunc="mean")
            ))
        # print(countdf)
def bestmethod(results):
    temp = (results.groupby(['data_type', 'cols', 'data_size','method'], as_index=False).apply(get_suitable2))
    # print(temp)
    temp.drop(temp.loc[(temp['base'] != '10')& (temp['base'] != '12')].index, inplace=True)
    temp.reset_index(drop=True, inplace=True)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        temp.drop(temp.loc[temp['method'] == 'timsort_n'].index, inplace=True)
        countdf = temp.groupby(['method','base']).agg(
            count=pd.NamedAgg(column="method", aggfunc="count"),                   
            ).reset_index()
        countdf['rank'] = countdf.groupby(['method'])[['count']].transform('rank','first',ascending=False).astype(int)
        countdf.sort_values(['method','rank'], inplace=True)
        countdf = countdf.pivot(index='rank', columns='method', values=['base','count'])
        countdf.columns = countdf.columns.swaplevel(0,1)
        countdf = countdf.sort_index(axis=1)
        # countdf = countdf.pivot(columns='method', values=['base', 'count'])
        countdf.rename(columns={'lsd_c':'lsd c','lsd_p':'lsd p','msd_c':'msd c','msd_p':'msd p'}, inplace=True)
        
        # print(countdf.to_latex(index=True,

        #           formatters={"name": str.upper},

        #           float_format="{:.1%}".format,))  

        
        counts = (temp.groupby(['method','base'],as_index=False)['method'].agg(['count']).sort_values(by=['method','count'], ascending=False).groupby('method').agg('first'))
        temp.sort_values(by=['times'], inplace=True)
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
def randvsrt(results, include='Few Unique'):
    exclude = ({include}^{'Few Unique', 'Nearly Sorted'}).pop()
    randomvsdiff = results.pivot(index=['cols','data_size','method','base'], columns='data_type', values='times').rename_axis(None, axis=1).reset_index().drop(exclude, axis=1)
    randomvsdiff['diff'] = (randomvsdiff['Random'] - randomvsdiff[include]) / randomvsdiff['Random']
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified    
        gp = (randomvsdiff.groupby(['method','data_size','cols'],as_index=False)['diff'].apply(lambda x:  np.mean(reject_outliers(x, m=3, dropna=True))))
        gp = gp.pivot(index=['cols','data_size'], columns='method', values='diff')
        # gp = gp.rename_axis(None, axis=1).reset_index()
        pd.options.display.float_format = '{:.1%}'.format
        gp.rename(columns={'lsd_c':'lsd c','lsd_p':'lsd p','msd_c':'msd c','msd_p':'msd p', 'timsort_n':'timsort'}, inplace=True)
        print(gp.mean(skipna=True))
        print(gp.to_latex(index=True,

                  formatters={"name": str.upper},

                  float_format="{:.1%}".format,

))  
        # exit()
        for gr, g in randomvsdiff.groupby(['method'],as_index=False):
            print(gr[0])

            # print((g.groupby(['cols'], axis=0)[['Nearly Sorted', 'Random']].apply(rejout)))
            gp = g.pivot(columns=['base'], index=['cols', 'data_size',], values='diff').reindex(natsort.natsorted(g['base'].unique()), axis=1)
            # gp = gp.rename_axis(None, axis=1).reset_index()
            # print()
            # print(gp.groupby(['cols'], axis=0)[['2','4','6','8','10','12','14','16']].agg({rejout}))

            gp =(gp.apply(reject_outliers, m=3, dropna=False, axis=1, result_type='broadcast'))

            gp['mean'] = gp.mean(axis=1, skipna=True)
            gp.loc['mean'] = gp.mean(skipna=True)
            print(gp)
            # print('')
def get_suitable2(g):
    if len(g)>1:
        from sklearn.cluster import KMeans
        from scipy import stats
        kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto")
        g['group'] = kmeans.fit_predict(g[['times']])
        g.sort_values(by=['times'], inplace=True)
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