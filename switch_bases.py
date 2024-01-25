import shutil

def copyfiles():
    names = ['lsd_c', 'lsd_p', 'msd_c', 'msd_p']
    for i in names:
        for j in range(4,16,2):
            shutil.copy2('/home/will/pypy2023/radixSort/'+i+'.py', '/home/will/pypy2023/radixSort/'+i+'_'+str(j)+'.py')
            
def base_switch():
    names = ['lsd_c', 'lsd_p']#, 'msd_c', 'msd_p']
    lines = [0,0,119,116]
    cutoffs = [2000,2000,2500,6400,12000,12000]
    for idx, i in enumerate(names):
        jdx = 0
        for j in range(6,18,2):
            fn = '/home/will/pypy2023/radixSortBetter/originals/'+i+'.py'
            with open(fn, 'r') as file:
                data = file.readlines()

            data[63] = '            self.base = '+str(j)+'\n'
            # if idx>1:
            #     data[lines[idx]] = '                    if (end - start) < '+str(cutoffs[jdx])+':\n'
            fn = '/home/will/pypy2023/radixSortBetter/'+i+'_'+str(j)+'.py'
            with open(fn, 'w') as file:
                file.writelines( data )
            jdx+=1
                

base_switch()
print("hello")