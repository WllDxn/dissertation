import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import rcParams
import numpy as np
import pandas as pd
import json
import seaborn as sns
import itertools
from scipy import stats
def reject_outliers_2(data, m=5):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev or 1.)
    return data[s < m]

def graph():
    #Input data
    with open('sort_times/insertion_tests_3_28.json') as f:
        data = json.load(f)
    methodnames = list(data['radix_sort'][0]['times'].keys())
    meta = [['times', x] for x in methodnames]
    df = pd.json_normalize(data['radix_sort'],meta=meta)
    df = df.reindex(sorted(df.columns), axis=1)
    
    #Prepare Data
    df.update(df.filter(like='times').applymap(reject_outliers_2))
    df.update(df.filter(like='times').applymap(np.mean))
    df.columns = df.columns.str.replace('times.', '')
    for method in methodnames:
        df[method] = df[method].astype(np.float32)
        df = df[np.abs(stats.zscore(df[method])) < 2]
        
    
    df = df.loc[df['data_size'] == 'med'].drop(['cols', 'rows', 'data_type', 'data_size'], axis=1)
    df = df.reset_index(drop=True)
    dfm = df.melt('threshold', var_name='method', value_name='time')
    dfm = dfm.astype({'method':str, 'time':np.float32})
    # gb = dfm.groupby('method')
    fig, ax = plt.subplots(figsize=(15, 30))
    palette = itertools.cycle(sns.color_palette())
    ax = sns.lmplot(data=dfm, x='threshold', y='time', hue='method', order=2,height=10, aspect=15/10, palette=palette, line_kws={'linewidth': 5.0, 'solid_capstyle': 'round', 'path_effects' :[pe.Stroke(linewidth=7, foreground='black', alpha=0.5), pe.Normal()]})
    ax.set_xlabels("Threshold",fontsize=20)
    ax.set_ylabels("Time",fontsize=20)
    plt.grid()
    # for method2 in df.columns.drop('threshold'):
    #     #ax = ax.scatter(df['threshold'], df[method2], marker=".")
    #     df[method2] = df[method2].astype(np.float64)
    #     col = next(palette)
        # ax = df.plot(x='threshold', y=method2, kind='scatter', figsize=(15, 8), grid=True)
        # plt.xlabel("Threshold")
        # plt.ylabel("Times")
    plt.savefig(f'graphs/insertion2024/temp.jpg')

graph()
