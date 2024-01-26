import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def reject_outliers_2(data, m=2):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev or 1.)
    return data[s < m]

def plot_regplot(df, x, y, color, label, scatter=True):
    try:
        sns.regplot(x=x, y=y, data=df[[x, y]].dropna(), order=2, ci=None, scatter_kws={"s": 80}, color=color, label=label, scatter=scatter)
        return True
    except Exception:
        return False

def graph():
    with open('sort_times_msdp_1.json', 'r') as f:
        dataset = json.load(f)
    df = pd.json_normalize(dataset['radix_sort'])
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.drop(['files', 'read', 'key', 'cols'], axis=1)
    df.update(df.filter(like='times').applymap(np.mean))

    for i in range(6, 18, 2):
        plt.cla()
        plot_names = [(f"insertion_{i}", 'r'), (f"radix_{i}", 'b'), (f"ranges{i}", 'g'), (f"ranges_doubled{i}", 'y')]
        fails = [
            name.split('_')[0]
            for name, color in plot_names
            if not plot_regplot(df, "rows", name, color, name)
        ]
        if fails:
            print(f'fails: {fails} base: {i}')
        if len(fails) < 4:
            plt.legend(fontsize=10)
            plt.savefig(f'a_msdpgraphs/msd_pig_{i}.jpg')

graph()
