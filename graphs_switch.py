import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_rows', 10)
def multiply(row):    
    if type(row['times'])is not float:
        row['method'] = row['times']['method']
        row['base'] = row['times']['base']
        row['times'] = row['times']['Times']
    return row
import ast 

def reject_outliers_2(data, m=2):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    # print(len(data))
    return data[s < m]
    # print(len(data))
    # print('---')
    # return data
import sys


if __name__=='__main__':
    dataset = {}
    dsize = ['lrg','med','sml']
    dsids = ['1,000,000','100,000','10,000']
    dsidsint = [1000000,100000,10000]
    sizes = {'large':9223372036854775807, 'med':4294967296, 'small': 1048576, 'tiny': 65536}

    for dsid, ds in enumerate(dsize):
        with open('switch_test.json', 'r') as f:
            dataset = json.load(f)
        df = pd.json_normalize(dataset['radix_sort'])
        df= df.reindex(sorted(df.columns), axis=1)
        try:
            df = df.drop(['files','read','key'], axis=1)
        except:
            None
        # df.drop(df[df.rows == 1000].index, inplace=True)
        df.drop(df[df.cols != dsidsint[dsid]].index, inplace=True)
        gb = df.groupby(['data_type'])
        plt.rcParams.update({'font.size': 22})
        # for sd in (True, False):
        for group in gb.groups:
            fig = plt.figure(figsize=(60,15),constrained_layout=True)
            rows = gb.get_group(group).rows.values[0]
            fig.suptitle(
                f'List length: {str(dsids[dsid])}'
                + '\nList count: '
                + str(rows)
                + '\nData type:'
                + str(group),
                fontsize='x-large',
            )

            df2 = gb.get_group(group).melt(id_vars=['data_type', 'data_size'],
                                                        var_name='method',
                                                        value_name='times')
            df2[['method', 'base']] = df2['method'].str.split('_base', expand=True)
            df2["method"] = df2["method"].apply(lambda x: x.replace("times.", "").replace("_sort", ""))
            df2 = df2.dropna()
            sgb=df2.groupby(['data_size'])
            if sgb.ngroups<1:continue
            subfigs = fig.subfigures(1, sgb.ngroups, hspace=20)
            # print((sgb.groups))
            for subgroup, (outerind, subfig) in zip(sgb.groups, enumerate(subfigs.flat)):
                df3=sgb.get_group(subgroup)
                #subfig.suptitle(f'Limit: {subgroup} - {sizes[subgroup]}')            
                methodgroups = df3.groupby(['method'])      
                try:           
                    axes = subfig.subplots(nrows=1, ncols=methodgroups.ngroups, sharey=True, width_ratios=methodgroups.size())                
                    targets = zip(methodgroups.groups.keys(), axes.flatten())       
                    # print(targets) 
                    for md, (key, ax) in  enumerate(targets):

                        mdf = methodgroups.get_group(key)
                    # print(mdf['base'])
                        #Axis = [sum(value)/len(value) for key, value in dictionary.items()]
                        mdf = mdf[mdf['base'] != '18']
                        ax.tick_params(axis='x', rotation=0)
                        my_cmap = plt.get_cmap("viridis")
                        # if sd:
                        mdf.loc[:,'times'] = mdf['times'].apply(reject_outliers_2)
                        # mdf["base"] = pd.to_numeric(mdf["base"])
                        mdf.sort_values(by=['base'], key=lambda x:x. str. len(), inplace=True)

                        xerrors = mdf['times'].apply(lambda x: np.std(x))
                        x = mdf['times'].apply(lambda x: np.mean(x))
                        # if group == 'Random' and key == 'lsd_counting':
                        #     # print(mdf)
                        #     # print('  ')
                        #     # print(mdf['times'])
                        #     # print('  ')
                        #     # print(x)
                        #     print('-------------------------')
                        ax.bar( mdf['base'],x, yerr= xerrors,color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5']if key!='tim'else ['C8'])
                        ax.set_xlabel(key)
                        if key=='tim':
                            ax.tick_params(axis='x', colors='white')                
                        if md!=0:
                            ax.tick_params(axis='y', left=False)
                            ax.spines["left"].set_visible(False)
                        else:
                            ax.set_ylabel('mean sort time (s)')
                        if md!=methodgroups.ngroups-1:
                            ax.spines["right"].set_visible(False)
                        ax.spines["top"].set_visible(False)
                except:
                    pass
            ext = ".jpg" #if sd else "_nonsd.jpg"
            filename = ds+group.replace(" ","_")
            url = "graphs/switch/"+filename+ext
            plt.savefig(url)
            print(filename)
            # for mg, (innerind, ax) in  zip(methodgroups.groups, enumerate(axs.flat)):
            #     mdf = methodgroups.get_group(mg)
            #     ax.set_title(mg, fontsize='small')                    
            #     ax.set_yticks([])
            #     ax.set_xticks([i for i in range(len(mdf.index))],labels=mdf['base'])  
            #     for base in mdf:                                     
            #         p = ax.bar(mdf['base'], x,width=0.8)
            #         ax.bar_label(p, mdf['base'])
        # #print(gb.get_group(group))  
        # df2 = gb.get_group(group).melt(id_vars=['data_type', 'data_size'],
        #                                             var_name='method',
        #                                             value_name='times')
        # df2[['method', 'base']] = df2['method'].str.split('_base', expand=True)
        # df2["method"] = df2["method"].apply(lambda x: x.replace("times.", ""))
        # sgb=df2.groupby(['data_size'])        
        # subfigs = fig.subfigures(1, sgb.ngroups)
        # for subgroup, (outerind, subfig ) in zip(sgb.groups, enumerate(subfigs.flat)):
        #     df3=sgb.get_group(subgroup)
        #     subfig.suptitle(f'Subfig {outerind}')            
        #     methodgroups = df3.groupby(['method'])
        #     axs = subfig.subplots(1, methodgroups.ngroups)
                           
        #     for mg, (innerind, ax) in  zip(methodgroups.groups, enumerate(axs.flat)):
        #         mdf = methodgroups.get_group(mg)
        #         x = mdf['times'].apply(lambda x: sum(x)/ len(x))
        #         ax.set_title(mg, fontsize='small')                    
        #         ax.set_yticks([])
        #         ax.set_xticks([i for i in range(len(mdf.index))],labels=mdf['base'])  
        #         for base in mdf:                                     
        #             p = ax.bar(mdf['base'], x,width=0.8)
        #             ax.bar_label(p, mdf['base'])


                

                    #ax.set_xticks(mdf['base'])
                    #print((mdf['times']).values)
                    #ax.set_yticks(sum(mdf['times'].values)/len(mdf['times'].values))
    # df = pd.DataFrame(dataset)
    # df = df.drop(columns=['rows', 'cols', 'files', 'read', 'key'])
    # print(df)
    # fn = lambda row: [{"method":x.split("_base")[0], "base": x.split("_base")[1], "Times": row['times'][x]} for x in row['times'].keys()]
    # col = df.apply(fn, axis=1)
    # df = df.assign(times=col.values).explode('times')
    # df = df.apply(multiply, axis=1)
    # gb = df. groupby('data_type')
    
    # for group in gb.groups:
    #     print(gb.get_group(group).reset_index())
    #     if 
    #     sgb = gb.get_group(group).groupby('data_size')
    #     for subgroup in sgb:
    #         print(sgb.get_group(subgroup))
    
 
        # fig, axes = plt.subplots(nrows=1, ncols=collength, figsize=(10,6), gridspec_kw=dict(hspace=0.4))
        # targets = zip(sgb.groups.keys(), axes.flatten())        
        # for i, (key, ax) in enumerate(targets):
        #     if dictionary!={}:
        #         xAxis = dictionary.keys()
        #         print(xAxis)
        #         yAxis = [sum(value)/len(value) for key, value in dictionary.items()]
        #         ax.tick_params(axis='x', rotation=90)
        #         ax.bar(xAxis, yAxis)
        #         ax.set_title(key)
                
        #ax.legend()
        
        #plt.show()
        #break
        # fig, axes = plt.subplots(nrows=1, ncols=3)
        # for idx, i in enumerate(coldDtypes):
    # df[3] = df[3].astype(object)
    # df.columns = ['data_type', 'data_size', 'times']
    # for data in dataset:
    #     df.pd.json_normalize(data['results'])
    
    
    # for dtype in data_types:
    #     plot_data = {}
    #     for dsize in data_sizes:
    #         for data in dataset:
    #             if data['data_size']==dtype and data['data_size']==dsize:
    #                 for method in data['times'].keys():
    #                     plot_data[dsize].setdefault(method,[])
    #                     plot_data[method].append(data['times'][method])
    #     for sub in plot_data:
    #         fig, axes = plt.subplots(nrows=1, ncols=len(data_sizes))  
    #         axes
                
        