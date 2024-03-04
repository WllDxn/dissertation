import os, subprocess, re
from natsort import natsorted
pypy_version = 'workingfinal'
def get_all_methods():
    tempv = os.listdir("/home/will/dissertation/pypy_versions")
    return {
        v: natsorted([x[: -len(v) - 1] for x in tempv if x.endswith(v)])
        for v in [pypy_version]
    }

for method in get_all_methods()[pypy_version]:
    b = re.findall(r'\d+', method)[0]
    if '_6' not  in method:continue
    p = f"/home/will/dissertation/pypy_versions/{method}_{pypy_version}/bin/pypy correctnesstest.py {b}"
    print(p)
    subprocess.run(p, shell=True,  cwd="/home/will/dissertation/minor_files")