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
    max_value = get_max_value(data_size)
    lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    lis[0] = threshold if threshold is not None else lis[0]

    if type == "Random":
        return lis
    elif type == "Few Unique":
        return np.random.choice(lis[: len(lis) // 10], cols).tolist()
    elif type == "Sorted":
        lis.sort()
        return lis
    elif type == "Reverse Sorted":
        lis.reverse()
        return lis
    elif type == "Nearly Sorted":
        for idx1 in range(len(lis) - 2):
            if random.random() < 0.1:
                lis[idx1], lis[idx1 + 1] = lis[idx1 + 1], lis[idx1]
        return lis


# with open("/home/will/dissertation/minor_files/arr.txt", "w+") as f:
#     for j in range(10):
#         arr = gen_list(10, 'large', "Random")
#         for i in arr:
#             f.write(str(i)+',')
#         f.write('\n')
for k in range(1, 1001):
    with open(f"/home/will/dissertation/minor_files/compareCompiledArrs/arr{k}.txt", "w+") as f:
        arr = gen_list(1000000, 'large', "Random")
        for i in arr:
            f.write(str(i)+',')
        print(k)
        
# with open("/home/will/dissertation/minor_files/arrm.txt", "w+") as f:
#     arr = gen_list(5, 'med', "Nearly Sorted")
#     for i in arr:
#         f.write(str(i)+',')