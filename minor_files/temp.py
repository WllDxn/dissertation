import subprocess, itertools
def execute(methodname, tim=False):
    print(f'----------------------------{methodname}----------------------------')
    if not tim:
        methodname += '_production'
    path = f'/home/will/dissertation/pypy_versions/{methodname}/bin/pypy'
    print([path, 'pypyperf.py','-o', f'pyperf/{methodname}-p.json'])
    subprocess.run([path, 'pypyperf.py','-o', f'pyperf/{methodname}-k.json'])
# for method in itertools.product([10], ['msd','lsd'], ['c','p']):
for method in itertools.product([10,12,8,6,14,4,16,2], ['msd','lsd'], ['c','p']):
    execute(f'{method[1]}_{method[2]}_{str(method[0])}')
# execute('timsort_n_0', True)
