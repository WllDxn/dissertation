import numpy as np
import random
def get_max_value(data_size):
    return {
        "large": 9223372036854775807,
        "med": 4294967296,
        "small": 1048576,
        "tiny": 65536,
    }.get(data_size, 65536)

def gen_list(cols, data_size, type="Random", threshold=None):
    max_value = data_size if isinstance(data_size, int)  else get_max_value(data_size)
    lis = []
    if type == "Random":
        lis = np.random.randint((-max_value), max_value+1, cols, dtype=np.int64).tolist()
        lis.insert(0, max_value-1)
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

    lis[0] = threshold if threshold is not None else lis[0]
    return [int(x) for x in lis]
def save_arrs():
    for i in range(1, 64):
        with open(f"/home/will/dissertation/minor_files/arrs/arr{i}.txt", "w+") as f:
            arr = gen_list(10000, int(pow(2,i)-1), "Random")
            for j in arr:
                f.write(str(j)+',')
save_arrs()