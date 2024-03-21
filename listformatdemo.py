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
ns = lis[:]
rd = np.random.randint(0, lislen, lislen).tolist()
for idx1 in range(len(ns) - 2):
    if random.random() < 0.25:
        ns[idx1], ns[idx1 + 1] = ns[idx1 + 1], ns[idx1]
fu = np.random.choice(rd[: len(rd) // 10], lislen).tolist()
xl = [str(idx) for idx, x in enumerate(ns)]
colorg = (x for x in sns.color_palette("muted", 3))
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