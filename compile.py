import subprocess
import re
import os
def test():
    None
def compile(sortnames, radixSort):
    names = ['lsd_p']#,'msd_p']
    cg = "\/tmp([^']*)"
    for ver in ['fixed_base']:#['insertion_always', 'insertion_disabled']:       
        for j in range(10,12,2):
            for i in names:
                #if (i=='msd_c'or i=='lsd_p') and j==12:continue
                # filename = sortnames+ver+'/'+i+'_'+str(j)+'.py'
                filename = sortnames+'/'+i+'_'+str(j)+'.py'
                packagename =  i+'_'+str(j)+'_'+ver
                cmd_str= 'cp '+ filename + ' ' + radixSort
                subprocess.run(cmd_str, shell=True)
                print('---------------------------' + packagename + '------------------------------------------')
                cmd_str = 'pypy ../../rpython/bin/rpython --opt=jit'
                subprocess.run(cmd_str, shell=True, cwd='/home/will/pypy2023/pypy3.10-v7.3.15-src/pypy/goal')
                cmd_str = 'pypy ../tool/release/package.py --archive-name=pypy-'+packagename+' --without-_ssl'
                result = subprocess.check_output(cmd_str, shell=True, cwd='/home/will/pypy2023/pypy3.10-v7.3.15-src/pypy/goal')
                temp = result.decode("utf-8").strip()
                test = re.findall(cg, temp)[0]
                cmd_str = 'cp -r /tmp'+test+'/pypy-'+packagename+' /home/will/pypy2023/pypy_versions_2024/'+packagename
                subprocess.run(cmd_str, shell=True, cwd='/home/will/pypy2023/pypy3.10-v7.3.15-src/pypy/goal')

def compile_switch(sortnames, radixSort):
    names = ['lsd_p']#,'msd_p']
    cg = "\/tmp([^']*)"
    j=0
    for ver in ['switch']:#['insertion_always', 'insertion_disabled']:
            for i in names:
                #if (i=='msd_c'or i=='lsd_p') and j==12:continue
                filename = sortnames+'/'+i+'.py'
                # filename = sortnames+'/'+i+'_'+str(j)+'.py'
                packagename =  i+'_'+str(j)+'_'+ver
                cmd_str= 'cp '+ filename + ' ' + radixSort
                subprocess.run(cmd_str, shell=True)
                print('---------------------------' + packagename + '------------------------------------------')
                cmd_str = 'pypy ../../rpython/bin/rpython --opt=jit'
                subprocess.run(cmd_str, shell=True, cwd='/home/will/pypy2023/pypy3.10-v7.3.15-src/pypy/goal')
                cmd_str = 'pypy ../tool/release/package.py --archive-name=pypy-'+packagename+' --without-_ssl'
                result = subprocess.check_output(cmd_str, shell=True, cwd='/home/will/pypy2023/pypy3.10-v7.3.15-src/pypy/goal')
                temp = result.decode("utf-8").strip()
                test = re.findall(cg, temp)[0]
                exename = '/home/will/pypy2023/pypy_versions_2024/'+packagename
                cmd_str = 'cp -r /tmp'+test+'/pypy-'+packagename+' '+exename
                subprocess.run(cmd_str, shell=True, cwd='/home/will/pypy2023/pypy3.10-v7.3.15-src/pypy/goal')
                exc = exename+'/bin/pypy -m ensurepip'
                subprocess.run(exc, shell=True)
                exc = exename+'/bin/pypy -mpip install numpy'
                subprocess.run(exc, shell=True)



def numpy(inname):
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/pypy_versions_2024/'
    for method in ['msd']:#, 'lsd']:
        for sort in ['c','p']:
            for base in range(6,18,2):
                name = method + ('_'+sort) + ('_'+str(base)) + inname
                exc = dir_path+name+'/bin/pypy -m ensurepip'
                subprocess.run(exc, shell=True)
                exc = dir_path+name+'/bin/pypy -mpip install numpy'
                subprocess.run(exc, shell=True)
                exc = dir_path+name+'/bin/pypy temp.py'
                subprocess.run(exc, shell=True)
           
def numpymp(name):
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/pypy_versions_2024/'
    exc = dir_path+name+'/bin/pypy -m ensurepip'
    subprocess.run(exc, shell=True)
    exc = dir_path+name+'/bin/pypy -mpip install numpy'
    subprocess.run(exc, shell=True)   
    
         
import multiprocessing
def numpymphandler():
    jobs = []
    for method in ['msd', 'lsd']:
        for sort in ['c','p']:
            for base in range(6,18,2):
                jobs.append(method + ('_'+sort) + ('_'+str(base)) + '_furtherImproved')
    with multiprocessing.Pool(4) as p:
        p.map(numpymp,jobs)
        
if __name__ == '__main__':
    # compile('/home/will/pypy2023/radixSortBetter/originals', '/home/will/pypy2023/pypy3.10-v7.3.15-src/rpython/rlib/radixsort.py')
    compile_switch('/home/will/pypy2023/radixsort_switchbase', '/home/will/pypy2023/pypy3.10-v7.3.15-src/rpython/rlib/radixsort.py')
    # numpy()

            
            
                

