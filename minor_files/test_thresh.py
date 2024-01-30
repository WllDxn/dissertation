import numpy as np
import time
def gen_list(cols=1000000, data_size='med', type='Random', threshold=None):
    max_value = {'large':9223372036854775807, 'med':4294967296, 'small': 1048576, 'tiny': 65536}[data_size]
    lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    lis[0]=threshold if threshold is not None else lis[0]
    #---Random List---
    if type=='Random':
        return lis
av1 = []
av2 = []
for i in range(100):
    gen_list(cols=10000).sort()
for i in range(20):
    arr = gen_list(threshold=1000000)
    arr2 = gen_list(threshold=0)
    t1=time.time()
    arr.sort()
    t2=time.time()
    arr2.sort()
    t3=time.time()
    print(t3-t2,t2-t1)
    av1.append(t3-t2)
    av2.append(t2-t1)
print('---------------')
print(sum(av1)/len(av1), end='')
print(sum(av2)/len(av2))
