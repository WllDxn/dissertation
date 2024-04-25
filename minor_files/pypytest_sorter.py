import sys, time

if __name__ =='__main__':
    with open('/home/will/dissertation/minor_files/compareCompiledArrs/arr'+str(sys.argv[1])+'.txt','r') as f:
        curr = [int(x) for x in f.read().split(',') if x != '']
    t = time.perf_counter()
    curr.sort()
    print(time.perf_counter()-t)