from tabulate import tabulate
import sys

if __name__=="__main__":

    for j in range(1,3,1):
        with open(f'minor_files/a{j}.txt', 'r') as f:
            l=f.readlines()
            for ndx, n in enumerate(l):
                lists = []
                bins = []
                print((ndx, ndx*12, (12*(ndx+1))-1))
                for i in n.split('],['):
                    lists.append([int(x) for x in i.split(',')])
                    m = 3 if j==1 else 2
                    bins = [str(j)for j in range(len([int(x) for x in i.split(',')])-m,-1,-1)]
                with open(f'minor_files/table{j}.tex','a') as f:
                    head = ['val'] if j==1 else['']
                    f.write((tabulate(lists, headers=['title']+bins+head, tablefmt='latex')))
                    f.write(r'\tabularnewline')
