from operator import ilshift
import numpy as np
import random, sys, itertools
def gen_list(cols, max_value, type="Random", threshold=None, insert=False):
    lis = []
    if type == "Random" and not insert:
        lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    elif insert:
        lis = [int(x) for x in range(-cols//2, cols//2+1)][:cols]
        random.shuffle(lis)
    elif type == "Few Unique":
        lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
        lis = np.random.choice(lis[: len(lis) // 10], cols).tolist()
    elif type == "Sorted":
        lis = [int(x*(max_value/cols)) for x in list(range(-cols//2, (cols//2)+1))][:cols]
        # lis = [int(x) for x in range(-max_value, max_value, int((2*max_value)/cols))]
    elif type == "Reverse Sorted":
        lis = [int(x*(max_value/cols)) for x in list(range(cols//2,(-cols//2)-1, -1))][:cols]
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
    return [int(x) for x in lis]


def is_sorted(l):
    return all(l[i] <= l[i+1] for i in range(len(l) - 1))
if __name__ == '__main__':
    base = int(sys.argv[1])
    config = list(itertools.product((range(1,64)), [
        "Random",
        "Nearly Sorted",
        "Sorted",
        "Reverse Sorted",
        "Few Unique",
    ]))
    not_sorted = []
    # while not not_sorted:
    #     not_sorted = []
    for idx, (i, dtype) in enumerate(config):
        lis = gen_list(10000, pow(2, i), dtype)
        # lis += ([ -2042860899935176798,9221940222586915079, -1942850055420458296])
        lisc = lis[:]
        lis.sort()
        if not is_sorted(lis):
            not_sorted.append((i, dtype, lis, lisc))
        print(f'{idx} {len(list(config))} {i} {dtype}', end='\r')
        del lis
    print('\033[2K', end='\r')
    # for i in not_sorted:
    #         print(i)
    print(f'Not sorted {len(not_sorted)}/{len(list(config))}')
        
        