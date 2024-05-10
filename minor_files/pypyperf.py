import pyperf
import math
def gen_list(cols, max_value, type="Random", insert=False, nearlysorted_percentage=10):
    lis = []
    if type == "Random" and not insert:
        s= f'np.random.randint(-{max_value}, {max_value}-1, {cols}, dtype=np.int64).tolist()'
    elif type == "Few Unique":
        s = f'np.random.randint(-{max_value}, {max_value}-1, {cols}, dtype=np.int64).tolist();lis = np.random.choice(lis[: len(lis) // 10], {cols}).tolist()'        
    elif type == "Sorted" or insert:
        s = f'[int(x*({max_value}/{cols})) for x in list(range(-{cols}//2,({cols}//2)+1, 1))][:{cols}]'
    elif type == "Reverse Sorted":
        s = f'[int(x*({max_value}/{cols})) for x in list(range({cols}//2,(-{cols}//2)-1, -1))][:{cols}]'
        # lis = [int(x) for x in range(max_value, -max_value-1, int(-(2*max_value)/cols))]
    elif type == "Nearly Sorted":
        s = f'''lis = [int(x*({max_value}/{cols})) for x in list(range(-{cols}//2,({cols}//2)+1, 1))][:{cols}]; 
for _ in range(int(len(lis)//(100/max(1, {nearlysorted_percentage})))):
    idx1 = random.randint(0, len(lis)-2);
    lis[idx1], lis[idx1 + 1] = lis[idx1 + 1], lis[idx1]'''
    return s
import sys, itertools,random
runner = pyperf.Runner()
# variations = list(itertools.product(["Random", "Few Unique", "Nearly Sorted" ],[100000],[63,48, 32,16]))
nl = r'\n'
variations = list(itertools.product(["Random","Few Unique"],[10000],[63]))
# print(variations)
for (typ, cols, m) in variations:
    max_value = int(math.pow(2, m))
    s = gen_list(cols, max_value, typ)
    # print(f"import numpy as np;import random;lis = {s};s = [x for x in lis]")
    runner.timeit(name=f"{cols},{m},{typ}",
                stmt=f'lis = {s};s = [x for x in lis];s.sort();',
                setup=f"import numpy as np;import random;",
               )
    
    """/home/will/dissertation/pypy_versions/lsd_c_10_production/bin/pypy -mpyperf timeit -s 'import numpy as np;import random;lis = np.random.randint(-9223372036854775808, 9223372036854775808-1, 100000, dtype=np.int64).tolist();s = [x for x in lis]' 's.sort()' -o 'pyperf/lsd_c_10_production-mil2.json' --rigorous"""
    