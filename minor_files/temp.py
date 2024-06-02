import subprocess, itertools
def execute(methodname, tim=False):
    print(f'----------------------------{methodname}100k----------------------------')
    if not tim:
        methodname += '_production'
    path = f'/home/will/dissertation/pypy_versions/{methodname}/bin/pypy'
<<<<<<< HEAD
    subprocess.run([path, 'pypyperf.py','-o', f'pyperf/{methodname}-100k.json'])
def executem(methodname, tim=False):
    print(f'----------------------------{methodname}mil----------------------------')
    if not tim:
        methodname += '_production'
    path = f'/home/will/dissertation/pypy_versions/{methodname}/bin/pypy'
    subprocess.run([path, 'pypyperfm.py','-o', f'pyperf/{methodname}-m.json'])
    
# for method in itertools.product([10], ['msd','lsd'], ['c','p']):
for method in itertools.product([10,12,8,6,14,4,16,2], ['msd','lsd'], ['c','p']):
=======
    print([path, 'pypyperf.py','-o', f'pyperf3/{methodname}.json'])
    subprocess.run([path, 'pypyperf.py','-o', f'pyperf3/{methodname}.json'])
# for method in itertools.product([10,12,8,6,14,4,16,2], ['msd','lsd'], ['c','p']):
for method in itertools.product([10,12], ['msd','lsd'], ['c','p']):
>>>>>>> 973111a5adcefb4496f7fe179d919ad63794f34e
    execute(f'{method[1]}_{method[2]}_{str(method[0])}')
for method in itertools.product([10,12,8,6,14,4,16,2], ['msd','lsd'], ['c','p']):
    executem(f'{method[1]}_{method[2]}_{str(method[0])}')

# execute('timsort_n_0', True)
