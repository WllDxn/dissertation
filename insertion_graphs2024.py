import pandas as pd
import matplotlib.pyplot as plt

def reject_outliers_2(data, m=2):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev or 1.)
    return data[s < m]

def graph():
    df = pd.read_json('sort_times/insertion_tests_24.json')
    df = df['radix_sort'].apply(pd.Series)
    df = df.reindex(sorted(df.columns), axis=1)
    df.update(df.filter(like='times').applymap(reject_outliers_2))
    df.update(df.filter(like='times').applymap(np.mean))
    df = df.loc[df['data_size'] == 'small'].drop(['cols', 'rows', 'data_type', 'data_size'], axis=1)
    df.columns = df.columns.str.replace('times.', '')
    df = df.reset_index(drop=True)

    for method in df.columns.drop('threshold'):
        df.plot(x='threshold', y=method, kind='scatter', figsize=(15, 8), grid=True)
        plt.xlabel("Threshold")
        plt.ylabel("Times")
        plt.savefig(f'graphs/insertion2024/{method}.jpg')

graph()
