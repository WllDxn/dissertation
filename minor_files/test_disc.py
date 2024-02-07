from print_bits import *
import subprocess
import os
def import_list():
    with open('/home/will/dissertation/minor_files/arr.txt', 'r+') as f:
        l = [int(x) for x in f.read()[:-1].split(',')]
        l.sort()
    splitted = str(l)[1:-1].split(', -1, -1')


    out = [[],[],[]] if splitted[2]==', 0' else [[],[]]

    count = 3 if splitted[2]==', 0' else 2
    for idx, i in enumerate(splitted):
        curr = [int(x.strip()) for x in i.split(',') if x.strip() != '']
        if curr != []:
            out[((idx)%count)].append(curr)
    out[-1] = [x[0] for x in out[-1]]
    return out
def my_sorted(l):
    return (all(l[i] <= l[i+1] for i in range(len(l) - 1)))

def get_lists(lists=None, discs=None):    
    inp = import_list()
    return (lists, discs)

def gen_lists():
    if os.stat("/home/will/dissertation/minor_files/arr.txt").st_size == 0:
        cmd_str = "python minor_files/gen_arr.py"
        subprocess.run(cmd_str, shell=True)
    lists, vals, discs = import_list()
    # for idx, list in enumerate(lists):
        # print_arr(list+[discs[idx]], num=idx, usedisc=True)
    # print('=====================================================')

    # for idx, list in enumerate(lists):
    #     print_arr(list+[discs[idx]], num=idx, usedisc=False, tempdisc=discs[idx])
    # print('===============================================================================================================================================================')
    with open('minor_files/table1.tex','w') as f:
        f.write(r"\documentclass{article}\begin{document}\hoffset=-1in\voffset=-1in\setbox0\hbox{\begin{tabular}[t]{|c|}")
    with open('minor_files/table2.tex','w') as f:
        f.write(r"\documentclass{article}\begin{document}\hoffset=-1in\voffset=-1in\setbox0\hbox{\begin{tabular}[t]{|c|}")
    with open('minor_files/a1.txt', 'w') as f:
        f.write('')
    with open('minor_files/a2.txt', 'w') as f:
        f.write('')
    for idx, list in enumerate(lists):
        
        a1 = print_arr(list, base=1, usedisc=False, tempdisc=discs[idx], num=idx, vals=vals[idx])
        a2 = print_arr(vals[idx],base=1, usedisc=False, num=idx)
        print(discs[idx])
        with open('minor_files/a1.txt', 'a') as f:
            f.write(str(a1).replace(" ", "")[2:-2])
            f.write('\n')
        with open('minor_files/a2.txt', 'a') as f:
            f.write(str(a2).replace(" ", "")[2:-2])
            f.write('\n')
        print('=====================================================')
    cmd_str = "python minor_files/print_table.py"
    subprocess.run(cmd_str, shell=True)
    with open('minor_files/table1.tex','a') as f:        
        f.write(r"\end{tabular}  }\pdfpageheight=\dimexpr\ht0+\dp0\relax\pdfpagewidth=\wd0\shipout\box0\stop")
    with open('minor_files/table2.tex','a') as f:        
        f.write(r" \end{tabular} }\pdfpageheight=\dimexpr\ht0+\dp0\relax\pdfpagewidth=\wd0\shipout\box0\stop")
    # for i in range(len(lists)):
    #     print(lists[i], vals[i], discs[i])
    # for idx, list in enumerate(vals):
    # for idx, list in enumerate(lists):
    #     print_arr(list+[discs[idx]], num=idx, min_bytes=63, base=1, usedisc=False)
    print(~((1 << int_bytes(-4045345, 2)- 1) - 1))
gen_lists()

