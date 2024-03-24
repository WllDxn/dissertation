import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
import natsort
import os
import re
import random

lislen=50
lis = [int(x) for x in range(lislen)]
ns = [int(x) for x in range(100)]
rd = np.random.randint(0, lislen, lislen).tolist()
for _ in range(int(len(ns)//(100/5000))):
    idx1 = random.randint(0, len(ns)-2)
    ns[idx1], ns[idx1+1] = ns[idx1+1], ns[idx1]
# df = pd.DataFrame({'data':ns})
# df['value'] =  pd.qcut(df['data'], 1000)
# for idx1 in range(len(ns) - 2):
#     if random.random() < 0.25:
#         ns[idx1], ns[idx1 + 1] = ns[idx1 + 1], ns[idx1]
fu = np.random.choice(rd[: len(rd) // 10], lislen).tolist()
xl = [str(idx) for idx, x in enumerate(ns)]
colorg = (x for x in sns.color_palette("muted", 3))
# print(df)
plt.axis('off')
s = [ns[x] for x in range(0,len(ns), len(ns)//100)]
x2 = [str(idx) for idx, x in enumerate(s)]
sns.barplot(x=x2, y=s, color=next(colorg))

# bp = sns.barplot(data=df,  x='value', y='data',  color=next(colorg))
plt.show()
exit()
f, axes = plt.subplots(1, 3, sharey=True, figsize=(12, 4))
for idx, data in enumerate([(ns,'Nearly Sorted'), (fu, 'Few Unique'), (rd, 'Random')]):
    bp = sns.barplot(x=xl, y=data[0], color=next(colorg), ax=axes[idx])
    bp.set(xticklabels=[])
    bp.tick_params(bottom=False)
    if idx == 1:
        bp.set_xlabel('Item')
    bp.set_ylabel('Value',rotation='horizontal', labelpad=20)
    bp.set_title(data[1])
plt.savefig(f'dissertation/demographs/demo.png', dpi=300, bbox_inches='tight')
plt.close()