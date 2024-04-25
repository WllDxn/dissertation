import time
def entry_point(argv):
    ts = []
    for i in range(1, 101):
        with open('/home/will/dissertation/minor_files/compareCompiledArrs/arr'+str(i)+'.txt','r') as f:
            # while True:
            curr = [int(x) for x in f.read().split(',') if x != '']  
            t = time.time()
            curr.sort()
            t1 = time.time()-t
            print(t1)
            ts.append(t1)
    s = 0
    for i in ts:
        s+=i
    print('---------\nAverage: '+str(s/len(ts)))

            
        
    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point
if __name__ == "__main__":
    entry_point(None)