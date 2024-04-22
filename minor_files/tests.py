
import time, random, math
def entry_point(argv):
    t, t1 = time.time(), time.perf_counter()
    for i in range(4):
        print(i)
        a = [random.randint(-int(math.pow(2,32)),int(math.pow(2,32))) for _ in range(1000000)]
        print(sorted(a)==a,end='')
        a.sort()
        print(sorted(a)==a)
    t2, t3 = time.time()-t, time.perf_counter()-t1
    print(f'{t2}\n{t3}')

    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point
if __name__ == "__main__":
    entry_point(None)