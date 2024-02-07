import os, subprocess
def get_lists():
    lists = []
    discs = []
    with open('/home/will/dissertation/minor_files/arr.txt', 'r+') as f:
        l = [int(x) for x in f.read()[:-1].split(',')]
        l.sort()
    return l
        
if os.stat("/home/will/dissertation/minor_files/arr.txt").st_size == 0:
    cmd_str = "python minor_files/gen_arr.py"
    subprocess.run(cmd_str, shell=True)
    s = True
    while s:
        l = get_lists()
        s = (all(l[i] <= l[i+1] for i in range(len(l) - 1)))
        cmd_str = "python minor_files/gen_arr.py"
        subprocess.run(cmd_str, shell=True)
        print(l)