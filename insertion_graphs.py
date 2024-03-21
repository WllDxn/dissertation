from turtle import title
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import rcParams
import numpy as np
import pandas as pd
import json
import seaborn as sns
import itertools
from scipy import stats
import re
import natsort
def reject_outliers_2(data, m=4):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev or 1.)
    return data[s < m]

def get_data(inp, threshold, maxc=2000):
    #Input data#
    with open(f'sort_times/{inp}') as f:
        data = json.load(f)

    methodnames = list(data['radix_sort'][0]['times'].keys())

    meta = [['times', x] for x in methodnames]

    df = pd.json_normalize(data['radix_sort'],meta=meta)
    df = df.reindex(sorted(df.columns), axis=1)
    #Prepare Data
    df.columns = df.columns.str.replace('times.', '')
    drop = [] if threshold==False else ['cols']
    df = df.drop(drop +[ 'rows', 'data_type', 'data_size'], axis=1)
    df = df.reset_index(drop=True)
    melt = 'cols' if threshold==False else 'threshold'
    dfm = df.melt(melt, var_name='method', value_name='time')
    dfm.dropna(inplace=True)
    dfm['time'] = dfm['time'].apply(reject_outliers_2)
    dfm['time'] = dfm['time'].apply(np.mean)
    dfm['time'] = dfm['time'].astype(np.float32)
    # dfm = dfm[np.abs(stats.zscore(dfm['time'])) < 3]
    # for method in methodnames:
    #     df.update(df[method].apply(reject_outliers_2))
    #     df.update(df[method].apply(np.mean))
    #     df[method] = df[method].astype(np.float32)
    #     z = np.abs(stats.zscore(df[method]))
    #     t = 3
    #     outliers = df[z > t]
    #     # df = df.drop(outliers.index)
    #     df = df[np.abs(stats.zscore(df[method])) < 2]

    # df.fillna(-1.0, inplace=True)   
    # df.rename(columns=lambda x: re.match(r'(l|m)(sd_)(c|p)(_\d+)', x).group(0), inplace=True)
    dfm['insert'] = dfm['method'].apply(lambda x: 'always' if 'always' in x else 'never')
    dfm['method'] = dfm['method'].apply(
        lambda x: re.match(r'(l|m)(sd_)(c|p)(_\d+)', x)[0]
    )
    # a = [f'msd_p_{t}' for t in range(10, 12, 2)]
    # dfm = dfm[dfm['method'].isin(a)]
    # print(dfm[dfm['insert'].isin(['always'])])
    # print(dfm)
    if maxc:
        dfm = dfm[dfm['cols'] <= maxc]
    return dfm.astype({'method':str, 'time':np.float32})
import copy
def graph(nn=0, threshold=False):
    plt.rcParams.update({'font.size': 20})
    # plt.rcParams.update({'': 20})
    plt.rcParams['text.usetex'] = True
    plt.rcParams['axes.formatter.limits'] = [-2,6]
    plt.rcParams['ytick.major.pad'] = 0
    melt = 'cols' if threshold==False else 'threshold'
    # dfms = []
    # for t in ['always', 'never']:
    #     fname = (
    #         f'{t}_insert_update_5.json'
    #     )
    #     # fname = 'thresh_insert_update_9.json'
    #     dfnew = get_data(fname, threshold)
    #     # dfnew['insert'] = t
    #     dfms.append(dfnew)

    
    # # dfms[0] = dfms[0][dfms[0][melt].isin(list(dfms[1][melt]))]
    # dfm = pd.concat(dfms)
    
    # dfm = get_data('workingfinal_alwaysinsert_workingfinal_neverinsert_4.jsonworkingrinsert_0.json', threshold)
    
    dfm = get_data(f'workingfinal_alwaysinsert_workingfinal_neverinsert_{nn}.json', threshold)
    # print(dfm)
    dfm.sort_values(by=['method'], inplace=True)
    dfm.sort_index(inplace=True)
    gb = dfm.groupby('method')
    
    output = {}
    
    for group in gb.groups:
        plt.clf()
        plt.close()
        df = gb.get_group(group)
        fig, ax = plt.subplots(figsize=(15, 30))
        palette = itertools.cycle(sns.color_palette())
        val = 0
        dict = {}
        if 'c' in group:
            dict = {
                2:400,
                4:100,
                6:100,
                8:100,
                10:200,
                12:400,
                14:1000,
                16:2000
            }
            val = dict[int(re.findall(r'\d+', group)[0])]
        else:
            dict = {
                2:750,
                4:500,
                6:400,
                8:400,
                10:400,
                12:500,
                14:1000,
                16:2000
            }
            val = dict[int(re.findall(r'\d+', group)[0])]

            
        df = df.loc[df[melt]<=val]
        always_poly = np.polyfit(df.loc[df['insert']=='always'][melt], df.loc[df['insert']=='always']['time'], 2)        
        never_poly = np.polyfit(df.loc[df['insert']=='never'][melt], df.loc[df['insert']=='never']['time'], 2)
        roots = np.roots(np.asarray(never_poly)-np.asarray(always_poly))
        roots= [x for x in roots if x>=0 and x<val]
        if len(roots)>1:
            roots.sort()
            roots = [roots[-1]]
        output[group] = roots[0]
        ry = np.polyval(always_poly, roots)
        df['insert'] = df['insert'].str.replace('always','Insertion')
        df['insert'] = df['insert'].str.replace('never','Radix')
        # plt.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))
        ax = sns.lmplot(data=df, x=melt, y='time',  hue='insert', legend=False, order=2,height=8, aspect=15/10, palette=palette, line_kws={'linewidth': 5.0, 'solid_capstyle': 'round', 'path_effects' :[pe.Stroke(linewidth=7, foreground='black', alpha=0.5), pe.Normal()]}, )        
        next(palette)
        plt.vlines(x=roots, ymin=0, ymax=ry, color=next(palette),linestyles='dashed')
        plt.plot(roots,ry, 'rD', alpha=0.75, mec='#9d1c00', mew=1)
        plt.text(roots[0], 0, '\n' + str(int(np.round(roots[0]))), linespacing= 0.25, color='r', horizontalalignment='center', verticalalignment='top')
        
        for g in ax.axes.flatten():
            # ival = 3 if len(str(g.get_xticks()[1]))<3 else 4
            # print(group, ival, str(g.get_xticks()[0]), len(str(g.get_xticks()[1])))
            # interval = (g.get_xticks()[1] - g.get_xticks()[0])/ival
            for idx, tick in enumerate(g.get_xticks()):
                if tick>roots[0]:
                    interval = abs((g.get_xticks()[0])/(6-len(str(int(roots[0])))))
                    if group=='msd_c_2':    
                        print(group, int(roots[0]), interval, tick, g.get_xticks()[idx-1])
                    if tick<roots[0]+interval:
                        g.get_xticklabels()[idx-1].set_color('w')
                    if g.get_xticks()[idx-1]>roots[0]-interval:
                        g.get_xticklabels()[idx-1-1].set_color('w')
                    break
            # g.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))


        # sns
        # if '14' not in group and '16' not in group and 'c' in group:
        #     ax.set(xlim=(0, 500))
        #     ax.set(ylim=(0,(float(max()))))
            # ax.set(ylim=(0, ))
        # ax.set(ylim=(mi, ma))

        # r = df.loc[np.logical_and(df[melt] < 5000, df[melt] >=0)]
        # ax.set_xlabels('List items',fontsize=20)
        # ax.set_ylabels("Time",fontsize=20)
        ax.set_xlabels('List items')
        ax.set_ylabels("Time")
        ax.set(ylim=(0,None))
        ax.set(xlim=(0,None))
        # ax.legend.set_title("Sort Method")
        
        
        titleinfo = group.split('_')

        base = f'$2^{{ {titleinfo[2]} }}$'
        ax.figure.suptitle(f'{titleinfo[0].upper()} {("Counting sort" if titleinfo[1]=="c" else "Pigeonhole sort")} base {base}')

        # ax.legend.set_title("Insertion", prop={'size': 20})
        # for text in ax.legend.get_texts():
        #     text.set_fontsize(18)
        # ax.legend.set_draggable(True)
        plt.grid()
        if group in [f'msd_{x}_{t}' for t in range(2,18,2) for x in ['p', 'c']]:
            plt.savefig(f'dissertation/insertion/{group}.png', dpi=300,bbox_inches='tight')
            print(f'{group}.png')
        plt.close()
    print('-'*32)
    for i in natsort.natsorted(output.keys()):
        print(f'{i}  \t-\t{int(np.round(output[i]))}')
        if i=='msd_c_16':
            print('')
    # for method2 in df.columns.drop('threshold'):
    #     #ax = ax.scatter(df['threshold'], df[method2], marker=".")
    #     df[method2] = df[method2].astype(np.float64)
    #     col = next(palette)
        # ax = df.plot(x='threshold', y=method2, kind='scatter', figsize=(15, 8), grid=True)
        # plt.xlabel("Threshold")
        # plt.ylabel("Times")
    

if __name__=="__main__":
    # graph('never_insert_0.json')
    for i in range(11,12):
        if i==3 or i==7 or i==5 or i==10 :continue
        try:
            graph(i)
            break
        except Exception as e:
            print(e)
            pass
        
    