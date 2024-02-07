
import time
import cProfile
import re
import numpy as np
def get_max_value(data_size):
    return {
        "large": 9223372036854775807,
        "med": 4294967296,
        "small": 1048576,
        "tiny": 65536,
    }.get(data_size, 65536)

def gen_list(cols, data_size, type="Random", threshold=None):
    max_value = get_max_value(data_size)
    lis = []
    if type == "Random":
        lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    elif type == "Few Unique":
        lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
        lis = np.random.choice(lis[: len(lis) // 10], cols).tolist()
    elif type == "Sorted":
        lis = [int(x*(max_value/cols)) for x in list(range(-cols//2,(cols//2)+1, 1))]
        
        # lis = [int(x) for x in range(-max_value, max_value, int((2*max_value)/cols))]
    elif type == "Reverse Sorted":
        lis = [int(x*(max_value/cols)) for x in list(range(cols//2,(-cols//2)-1, -1))]
        # lis = [int(x) for x in range(max_value, -max_value, int(-(2*max_value)/cols))]
    elif type == "Nearly Sorted":
        # lis = [int(x) for x in range(-max_value, max_value, int((2*max_value)/cols))]
        lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
        lis.sort()
        for idx1 in range(len(lis) - 2):
            if random.random() < 0.1:
                lis[idx1], lis[idx1 + 1] = lis[idx1 + 1], lis[idx1]
        # print(lis[:10])
    lis[0] = threshold if threshold is not None else lis[0]
    return lis


import cProfile, pstats, io
from pstats import SortKey

with open('/home/will/dissertation/minor_files/arr.txt', 'r+') as f:
    # l = [int(x) for x in f.read()[:-1].split(',')]
    l =  [int(x) for x in gen_list(100000, 'large', "Random")]
    l =  gen_list(100000, 'large', "Random")[:]
# ls = set([type(item) for item in l])
# t=time.time()
    pr = cProfile.Profile()
    pr.enable()
    l.sort()
    print(all(l[i] <= l[i+1] for i in range(len(l) - 1)))
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
