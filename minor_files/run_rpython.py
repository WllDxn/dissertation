import subprocess

cmd_str = "pypy ../../rpython/bin/rpython tests.py; ./tests-c"
subprocess.run(cmd_str, shell=True, cwd="/home/will/dissertation/pypy_misc/pypy3.10-v7.3.15-src/pypy/goal")
# cmd_str = "./test-c"
# subprocess.run(cmd_str, shell=True, cwd="/home/will/dissertation/pypy_versions/pypy3.10-v7.3.15-src/pypy/goal")