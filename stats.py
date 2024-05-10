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
import re

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
                df3 = sgb.get_group((subgroup,))
                subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                # print(df3.head(10))
                lim = np.mean(df3.loc[df3['method'] == 'timsort_n', 'times'].values[0])
                df4 = df3.copy()
                df4.loc[:,['times']] = df4['times'].apply(reject_outliers, m=3)
                df4['stdev'] = df4['times'].apply(lambda x: np.std(x,axis=None))
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

    return results.reset_index()
    

    # bestofbest(results)
    # normalr(results)
    # bestmethod(results)
def getcompare():
    with open('minor_files/compare2.txt', 'r+') as f:
        compare = f.readlines()

    methodbase = ([re.findall(r'.*_', i)[0][:-1].strip() for i in  compare[0].split('|') if '_' in i] )
    methodbase2 = ([(i[:5], int(i[6:])) for i in methodbase])
    sizedict = {'63': 'large', '32': 'med', '20': 'small','16':'tiny','48':'error'}
    rows_list = []
    for row in compare[2:-1]:
        values = (row.split('|')[1:-1])
        cols,size, typ = values[0].strip().split(',')
        if size=='48':continue
        values[1:] = [i if 'not' not in i else values[1] for i in values[1:] ]
        times = list(map(lambda x: float(x[:-2])/1000000 if 'u' in x else float(x[:-2])/1000, [(re.findall(r'^[^s]*', i.strip())[0]) for i in values[1:]]))
        times = list(map(lambda x: float(x[:-2])/1000000 if 'u' in x else float(x[:-2])/1000, [(re.findall(r'^[^s]*', i.strip())[0]) for i in values[1:]]))
        
        rows_list.extend(
            {
                'cols': int(cols),
                'data_size': sizedict[size],
                'data_type': typ,
                'method': methodbase2[i][0],
                'base': methodbase2[i][1],
                'methodbase':methodbase[i],
                'times': t,
            }
            for i, t in enumerate(times)
        )
    df = pd.DataFrame(rows_list)

    return df
    
_TIMEDELTA_UNITS = ('sec', 'ms', 'us', 'ns')
def format_timedeltas(values):
    ref_value = abs(values[0])
    for i in range(2, -9, -1):
        if ref_value >= 10.0 ** i:
            break
    else:
        i = -9

    precision = 2 - i % 3
    k = -(i // 3) if i < 0 else 0
    factor = 10 ** (k * 3)
    unit = _TIMEDELTA_UNITS[k]
    fmt = "%%.%sf %s" % (precision, unit)

    return tuple(fmt % (value * factor,) for value in values)


def format_timedelta(value):
    return format_timedeltas((value,))[0]

def bestofbest(results):
    # grafresults(results.drop(results.loc[results['data_type'] == 'Few Unique'].index))
    grafresults(results)
    print('-------------------')
    grafresults(results.drop(results.loc[results['data_type'] != 'Random'].index))
    print('-------------------')
    grafresults(results.drop(results.loc[results['data_type'] != 'Nearly Sorted'].index))
    # results.drop(results.loc[(results['method'] != 'timsort_n') & (results['method'] != 'lsd_p')].index, inplace=True)
    
def grafresults(results, showbest=True):
    if showbest:
        results.drop(results.index.difference(results.loc[((results['method'] == 'msd_c') & (results['base'] == '10')) 
                            | ((results['method'] == 'msd_p') & (results['base'] == '6'))
                            | ((results['method'] == 'lsd_c') & (results['base'] == '10'))
                            | ((results['method'] == 'lsd_p') & (results['base'] == '12'))
                            | (results['method'] == 'timsort_n')].index),inplace=True)
    
        
    # results['times'] = results.groupby(['data_type', 'cols', 'data_size'])[['times']].transform(lambda g: (g - np.mean(g)) / np.std(g,axis=0))
    
    results['cattime'] = results.sort_values(by='method',ascending=False).groupby(['data_type', 'cols', 'data_size'])['times'].transform('first')
    # results.loc[results['method']=='timsort_n','cattime'] = 1.0
    results['oldtime'] = results['times']
    # results['times'] = 100*((results['times']-results['cattime'])/((results['times']+results['cattime'])/2))
    # results['times'] = 100*((results['cattime']-results['times'])/(results['times']))
    results['times'] = 100*((results['times']-results['cattime'])/(results['cattime']))
    # results.loc[results['method']=='timsort_n','times'] = 0.0
    
    # print(results.loc[results['method']=='lsd_p'].sort_values(by='data_type'))
    # results['times'] = 100*((results['times'] - results.sort_values(by='method',ascending=False).groupby(['data_type', 'cols', 'data_size'])['times'].transform('first'))/results['times'])
    results['rank'] = (results.groupby(['data_type', 'cols', 'data_size']).agg(rank=pd.NamedAgg(column='times', aggfunc='rank'))['rank'].astype(int))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        # print(results.loc[results['method']=='timsort_n'])
        for cat in [ 'data_type','cols', 'data_size', '']:
            print(f'----------------{cat}---------------------')
            r = (results.groupby(['method','base',cat] if cat!='' else ['method','base']).agg(
                rank=pd.NamedAgg(column='rank', aggfunc='mean'),
                ranksum=pd.NamedAgg(column='rank', aggfunc='sum'),
                times=pd.NamedAgg(column='times', aggfunc='mean'),
                
                oldtime=pd.NamedAgg(column='oldtime', aggfunc='mean')
            ).sort_values(by=['method'], ascending=False).reset_index())
            # r['rank'] = np.round(r['rank'],2)
            r['rawtimes'] = r['times']
            r['times'] = r['times'].astype(int).astype(str) +'\%'
            r['rank'] = r['rank'].map("{:.2f}".format)
            # r['times'] = np.round(r['times'],2)
            
            if cat!='':
                # r['rawtimes'] = ((r.groupby(by='method')['rawtimes'].transform('mean')))
                # r['times'] =r['rawtimes'].astype(int).astype(str) +'\%'
                if showbest==True:
                    r=r.pivot(index='method', columns=cat, values=['rawtimes']).sort_values(by=['method'])
                else:
                    r=r.pivot(index=['method','base'], columns=cat, values=['rawtimes']).sort_values(by=['method','base'])
                # r['ave'] = r.groupby(by='method')['rawtimes'].transform('mean')
                r = r.droplevel(0,axis=1)
                r = r.rename_axis(None, axis=0) 
                r['Average'] = r.apply('mean',axis=1)
                r = r.astype(int).astype(str) +'\%'
                # r = r.sort_index(axis=1)
                print(r.to_latex(index=True,

                  formatters={"name": str.upper},
                
                  float_format="{:.4}".format,).replace('_n','').replace('_',' '))  
                print('\n')
                print(r)
                print('\n')
            else:
                if not showbest:
                    r.drop(r.loc[r['method']=='timsort_n'].index,axis=0,inplace=True)
                    r['rank'] = (r.sort_values(by='times').groupby(['method'])['rawtimes'].agg('rank')).astype('int')
                    r = r[['method','base','rank','rawtimes','times']].pivot(index='rank',columns='method',values=['base','times'])
                    r.columns = r.columns.swaplevel(0,1)
                    r = r.sort_index(axis=1)
                    print(r.to_latex(index=True,

                  formatters={"name": str.upper},
                
                  float_format="{:.4}".format,)) 
                    print('')
                    print(r)
                    # for gr, rg in r:
                    #     print(rg[['method','base','times']])
                    #     print('')
                else:  
                    print(r[['method','base','times']].sort_values(by='method'))
                    r
                    print(r[['method','times']].sort_values(by='method').to_latex(index=False,

                  formatters={"name": str.upper},
                
                  float_format="{:.4}".format,).replace('_n','').replace('_',' ')) 

                
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
        results['times'] = results.groupby(['data_type', 'cols', 'data_size','method'])[['times']].transform(lambda g: (g - np.mean(g)) / np.std(g,axis=None))
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

def graf(res):
    # print(results)
    pd.options.display.float_format = '{:,.6f}'.format
    res['methodbase'] = res['method']+'_'+res['base']
    res = (res.pivot(index=['data_type','data_size','cols'],columns=['methodbase'],values='times'))
    # comp = (getcompare().pivot(index=['data_type','data_size','cols'],columns=['method','base'],values='times'))
    # print(res)
    # print('')
    # print(comp)
    # print('')
    # res = res[comp.columns][res.index.isin(comp.index)]
    # pd.options.display.float_format = '{:,.1f}%'.format
    # div = res*100/comp
    # print(div)
    # print(np.mean([v for x in div.values for v in x]))
    # print(np.std([v for x in div.values for v in x]))
    dsize = ['lrg', 'med', 'sml']
    dsidsint = [1000000, 100000, 10000]
    sizes = {'large': 9223372036854775807, 'med': 4294967296, 'small': 1048576, 'tiny': 65536}
    results = []
    comp = getcompare()
    gb = comp.reset_index().groupby(['data_type'])
    plt.rcParams.update({'font.size': 26})
    for group, g in gb:
        df0 = g
        # print(df2)
        for kdx, k in enumerate([['large',''],['med',''],['small',''],['tiny','']]):
            df2 = df0.dropna().copy()
            if len(k)<4:
                df2.drop(df2.loc[(df2['data_size'] != k[0]) & (df2['data_size'] != k[1])].index, inplace=True)
            # print(df2)
            sgb = df2.groupby(['data_size'])
            fig = plt.figure(figsize=((7.5*sgb.ngroups)+4, 10), constrained_layout=True)

            fig.suptitle(f'List length: 10,000\nData type: {group[0]}', fontsize='x-large')
            if sgb.ngroups ==0:continue
            subfigs = fig.subfigures(1, sgb.ngroups, hspace=0.1)
            subfigs = subfigs.flatten() if sgb.ngroups > 1 else [subfigs]

            for subgroup, subfig in zip(sgb.groups, subfigs):
                df3 = sgb.get_group((subgroup,))
                subfig.suptitle(f'Limit: {sizes[str(subgroup)]:,}')
                # print(df3.head(10))                
                methodgroups = df3.groupby(['method'])
                mgroup = methodgroups.size()
                newmgroup = pd.Series()
                for idx, i in enumerate(methodgroups.groups.keys()):
                    newmgroup[i] = len(methodgroups.get_group((i,)))+0.25
                    newmgroup[str(idx)] = 0.25
                    
                # mgroup['timsort_n'] = 7.5
                axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups*2, sharey=True, width_ratios=newmgroup)
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
                    mdf = methodgroups.get_group((key,))                    
                    # mdf.loc[:,['times']] = mdf['times'].apply(reject_outliers, m=3)
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
                    xerrors = mdf['times'].apply(np.std,axis=None)
                    x = mdf['times'].apply(np.mean)                        
                    
                    # cllr = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5'] if not(group[0]=='Random' and subgroup=='tiny' and key=='msd_c') else ['C9' for _ in range(6)]
                    # print(mdf)

                    ax.bar(mdf['base'], x, width=1.6,  yerr=xerrors, color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5'] if 'timsort' not in key else 'C8')
                    if 'timsort' not in key:
                        ax.set_xlabel(key)
                        ax.tick_params(axis='x', labelsize= 22 if len(k)==1 else 16)
                        ax.set_xticks([2,4,6,8,10,12,14,16])
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
            # if stats: continue
            graphdir = Path('graphs') / Path('pyperf')
            os.makedirs(graphdir, exist_ok = True)
            graphdir.mkdir(parents=True, exist_ok=True)
            gname = str(group).replace(' ', '_').strip('(,)\'')
            filename = f"{10000}_{gname}_{kdx}.png"
            fig.set_constrained_layout_pads(w_pad=0, h_pad=0, hspace=0, wspace=0)
            plt.savefig(graphdir / filename, bbox_inches='tight')
            print(graphdir / filename)
            # plt.show()
            plt.close()
    # if stats: continue
    # graphdir = Path('graphs') / Path(fname).stem / Path('nopig') if prune else Path('graphs') / Path('winners') / Path(fname).stem 
    # os.makedirs(graphdir, exist_ok = True)
    # graphdir.mkdir(parents=True, exist_ok=True)
    # gname = str(group).replace(' ', '_').strip('(,)\'')
    # filename = f"{ds}_{gname}_nolp_{kdx}.png" if prune else f"{ds}_{gname}_{kdx}.png"
    # fig.set_constrained_layout_pads(w_pad=0, h_pad=0, hspace=0, wspace=0)
    
if __name__ == '__main__':
    # results = do_graph(reject_outliers, Path('/home/will/dissertation/sort_times_in_diss/production_0.json'))
    import pickle
    # with open('minor_files/df.pickle','wb') as f:
    #     pickle.dump(results, f)
    with open('minor_files/df.pickle','rb') as f:
        results = pickle.load(f)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified    
        grafresults(results)
        # res = (results.loc[(results['cols']==10000)  & ((results['base']=='10')|(results['base']=='12')) & ((results['data_type']=='Random') | (results['data_type']=='Few Unique')) & ((results['data_size']=='large')| (results['data_size']=='large'))]).sort_values(by=['method'])
        # res['times'] = res['times'].apply(format_timedelta)
        
