from tabulate import tabulate
from print_bits import print_arr
def tab(arr, min_bytes, base=1):
    out = [[] for _ in arr]
    for idx, i in enumerate(arr):
        for j in range(min_bytes):
            val = (i >> j*base) & 1
            out[idx].append(val)
        out[idx].reverse()
    return out
def g(val, s=None, min_bytes=None):
    return [val if s is None else s] + tab([val],min_bytes)[0]
val = -2305843009213693952
val = 102
bits = 8
i = []
i.append(g(val, min_bytes=bits))
i.append(g(~(val),f"~{val}", min_bytes=bits))
# i.append(g((val ^ ~(15)),f'{val} ^ ~15', bits))

head = ["Value"] + list(range(bits-1,-1,-1))
for idx, j in enumerate(i):
    i[idx] = j[:9]
head = head[:9]
with open('minor_files/bittable.tex','w') as f:
    f.write(tabulate(i,headers=head, tablefmt='latex'))