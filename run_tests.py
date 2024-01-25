import subprocess
def n(methodName):
    num = 50
    output = 'switch_test.json'
    for method in ['lsd']:
        for sort in ['p']:
            sortname = 'counting' if sort=='c' else method+'pigeonhole'
            baserange = list(range(8,18,4)) if methodName == 'working' else [0]
            for base in baserange:
                # if method == 'msd' and (sort=='c' or base <14): continue
                name = method + ('_'+sort) + ('_'+str(base)) + '_' + methodName
                formatname = method + ('_'+sortname+'_sort') + ('_base'+str(base)) 
                for l in [100000]:
                    exc = '/home/will/pypy2023/pypy_versions_2024/'+name+'/bin/pypy sort_timer_gendata_anymax.py -m ' + formatname + ' -o '+output+' -n '+str(num) + ' -l '+str(l)
                print('\033[1;35m')
                print(exc)
                print('')
                subprocess.run(exc, shell=True)
                print('--complete--')
                
    # exc = '/home/will/pypy2023/pypy_versions/timsort_furtherImproved/bin/pypy sort_timer_gendata.py -m tim_sort_base0 -o '+output +' -n '+str(num)
    # print('\033[1;35m')
    # print(exc)
    # print('')
    # subprocess.run(exc, shell=True)
    # print('--complete--')
  
def insertion():
    num = 100
    output = ['insertion2.json', 'insertion3.json', 'insertion4.json', ]
    lims = [1000, 5000, 1000]
    for lim in range(3):
        for method in ['msd']:
            for sort in ['c','p']:
                sortname = 'counting' if sort=='c' else method+'pigeonhole'
                for base in range(6,18,2):
                    #if method == 'msd' and (sort=='c' or base <14): continue
                    name = method + ('_'+sort) + ('_'+str(base)) + '_better_itest'
                    formatname = method + ('_'+sortname+'_sort') + ('_base'+str(base)) 
                    for l in [10000]:
                        exc = '/home/will/pypy2023/pypy_versions_2024/'+name+'/bin/pypy insertion_test.py -m ' + formatname + ' -o '+str(output[lim])+' -n '+str(num) + ' -l '+str(l) + '  -et "Nearly Sorted" Sorted "Few Unique" "Reverse Sorted" -t 0 ' +str(lims[lim])
                    print('\033[1;35m')
                    print(exc)
                    print('')
                    subprocess.run(exc, shell=True)
                    print('--complete--')
             


def n2():
    for method in ['msd', 'lsd']:
        for sort in ['c']:
            sortname = method+'count' if sort=='c' else method+'pigeonhole'
            for base in range(6,18,2):
                name = ('msd_'+sort) + ('_'+str(base))
                if method=='lsd':
                    name += ("_insertion_always")
                else:
                    name+= ("_insertion_disabled")
                for l in [1000000]:#,10000,1000]:
                    exc = '/home/will/pypy2023/pypy_versions/'+name+'/bin/pypy sort_timer.py -em ' + sortname +' -b ' + str(base) + ' -o sort_times_disabled.json -n 100 -l '+str(l)
                    print('\033[1;35m')
                    print(exc)
                    print('')
                    subprocess.run(exc, shell=True)
                
def ins():
    fil = 'sort_times_msdp_1.json'
    #r = [0,1500,2250,6275,12000,]
    r = [0, 0, 0, 0, 0, 0]
    t = [5000, 5000, 10000, 12000, 30000, 30000]
    for method in ['always', 'disabled']:
        for i in range(6,18,2):  
            st = r[(i-6)//2]
            ed = int((t[(i-6)//2]))
            #st = int((t[(i-6)//2]))
            #ed = st * 4         
            gap = (ed-st)//100
            newgap = (ed-st)//10 if ((method=='disabled' and i==16) or method=='always') else (ed-st)//100
            for l in range(st,ed,newgap):
            #for l in range(0,st+gap,gap):
                if method == 'always':
                    name = 'msd_p_'+str(i)+"_insertion_always"
                    m = 'lsdpigeonhole -b ' + str(i)
                elif method == 'disabled':
                    name = 'msd_p_'+str(i)+"_insertion_disabled"
                    m = 'msdpigeonhole -b ' + str(i)
                # elif method == 'ranges_doubled':
                #     name = 'msd_c_'+str(i)+"_insertion_ranges_doubled"
                #     m = 'msdpigeonhole -b ' + str(i)
                # else:
                #     name = 'msd_c_'+str(i)+"_insertion_ranges_copy"
                #     m = 'lsdpigeonhole -b ' + str(i)
                count = 10 if ((method=='disabled' and i==16) or method=='always') else 50
                exc = '/home/will/pypy2023/pypy_versions/'+name+'/bin/pypy sort_timer.py -es tiny small med -et "Few Unique" "Sorted" "Reverse Sorted" "Nearly Sorted" -em '+ m +' -o '+fil+' -n '+str(count)+' -l '+str(l)
                print('\033[1;35m')
                print(exc)
                print('')
                subprocess.run(exc, shell=True)
            
n('switch')
n('working')