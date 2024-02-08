import os
import subprocess
from compile import *
import random
sort_times = "/home/will/dissertation/sort_times"
methods = ["fewer_iters"]
# methods = ["always_insert"]
# methods=['insertion_tests_3']

def n(methodName, output, num=100):
    """
    Generates and runs a series of commands for sorting data based on the given method name.

    Args:
        methodName (str): The name of the method to use for sorting.
        output (str): The output location for the sorted data.
        num (int, optional): The number of data elements to sort. Defaults to 10.

    Raises:
        None

    Returns:
        None
    """

    fames = (
        get_files(f"{radixsort_location}/{methodName}")
        if methodName != "timsort"
        else ["/home/will/dissertation/pypy_versions/timsort"]
    )
    rg = "[/.+?\./]"
    for name in fames:
        # if 'c' in name:continue
        packagename = re.split(rg, name)[0] if methodName != "timsort" else "timsort"
        exepath = f'{pypy_versions}/{packagename}_{methodName}/bin/pypy'
        if not os.path.exists(exepath):continue
        for l in [10000, 100000, 1000000]:
            exc = f"{pypy_versions}/{packagename}_{methodName}/bin/pypy sort_timer_gendata.py -m {packagename} -o {output} -n {num} -l {str(l)}"
            print("\033[1;35m")
            print(exc)
            print("")
            subprocess.run(exc, shell=True)
            print("--complete--")


def get_filename(name):
    """
    Returns a unique filename based on the given name.

    Args:
        name (str): The base name for the filename.

    Raises:
        None

    Returns:
        str: A unique filename based on the given name.
    """

    path = os.path.join(sort_times, f"{name}_0.json")
    uniq = 0
    while os.path.exists(path):
        path = os.path.join(sort_times, f"{name}_{str(uniq)}.json")
        uniq += 1
    print(path)
    return path

def ins(methodName, output, thresh=256, threshdivs=128, num=50):
    """
    Generates and runs a series of commands for sorting data based on the given method name.

    Args:
        methodName (str): The name of the method to use for sorting.
        output (str): The output location for the sorted data.
        num (int, optional): The number of data elements to sort. Defaults to 10.

    Raises:
        None

    Returns:
        None
    """
    fames = (
        get_files(f"{radixsort_location}/{methodName}")
        if methodName != "timsort"
        else ["/home/will/dissertation/pypy_versions/timsort"]
    )
    rg = "[/.+?\./]"
    count=0
    for name in fames:
        
        # if ('8' not in name and '12'not in name and '16'not in name): continue
        packagename = re.split(rg, name)[0] if methodName != "timsort" else "timsort"
        exepath = f'{pypy_versions}/{packagename}_{methodName}/bin/pypy'
        if not os.path.exists(exepath):continue
        for l in [100000]:
            exc = f'{exepath} sort_timer_gendata.py -m {packagename} -o {output} -n {num} -l {str(l)} -t {thresh} -d {threshdivs} -et "Few Unique" "Sorted" "Reverse Sorted" "Nearly Sorted" -es tiny small large'
            print("\033[1;35m")
            print(exc)
            print("")
            subprocess.run(exc, shell=True)
            print("--complete--")
        count+=1
        # break
def ins_ll(methodName, output, num=100):
    """
    Generates and runs a series of commands for sorting data based on the given method name.

    Args:
        methodName (str): The name of the method to use for sorting.
        output (str): The output location for the sorted data.
        num (int, optional): The number of data elements to sort. Defaults to 10.

    Raises:
        None

    Returns:
        None
    """
    fames = (
        get_files(f"{radixsort_location}/{methodName}")
        if methodName != "timsort"
        else ["/home/will/dissertation/pypy_versions/timsort"]
    )
    rg = "[/.+?\./]"
    count=0
    for name in fames:
        # if ('6' not in name and '8' not in name and '10' not in name and'12' not in name) or '16' in name: continue
        if ('msd_p' not in name) or ('12' not in name or '16' in name): continue
        # if ('msd_p' not in name) or ('6' not in name and '8' not in name and '10' not in name and'12' not in name or '16' in name): continue

        packagename = re.split(rg, name)[0] if methodName != "timsort" else "timsort"
        exepath = f'{pypy_versions}/{packagename}_{methodName}/bin/pypy'
        if not os.path.exists(exepath):continue
        for l in [10000]:
            exc = f'{exepath} sort_timer_gendata.py -m {packagename} -o {output} -n {num} -l {str(l)} -et "Few Unique" "Sorted" "Reverse Sorted" "Nearly Sorted" -es tiny small large -s'
            print("\033[1;35m")
            print(exc)
            print("")
            subprocess.run(exc, shell=True)
            print("--complete--")
        count+=1

#  def ins(methodName, output, num=10):
#     fames = (
#         get_files(f"{radixsort_location}/{methodName}")
#         if methodName != "timsort"
#         else ["/home/will/dissertation/pypy_versions/timsort"]
#     )
#     rg = "[/.+?\./]"
#     for name in fames:
#         packagename = re.split(rg, name)[0]
#         for l in [50000 100000 150000 200000 250000]:
#             exc = f'{pypy_versions}/{packagename}_{methodName}/bin/pypy sort_timer_gendata_anymax.py -m {packagename} -o {output} -n {num} -l {str(l)} -et "Few Unique" "Sorted" "Reverse Sorted" "Nearly Sorted" '
#             print("\033[1;35m")
#             print(exc)
#             print("")
#             subprocess.run(exc, shell=True)
#             print("--complete--")
#     fil = "sort_times_msdp_1.json"
#     # r = [0,1500,2250,6275,12000,]
#     r = [0, 0, 0, 0, 0, 0]
#     t = [5000, 5000, 10000, 12000, 30000, 30000]
#     for method in ["always", "disabled"]:
#         for i in range(6, 18, 2):
#             st = r[(i - 6) // 2]
#             ed = int((t[(i - 6) // 2]))
#             # st = int((t[(i-6)//2]))
#             # ed = st * 4
#             gap = (ed - st) // 100
#             newgap = (
#                 (ed - st) // 10
#                 if ((method == "disabled" and i == 16) or method == "always")
#                 else (ed - st) // 100
#             )
#             for l in range(st, ed, newgap):
#                 # for l in range(0,st+gap,gap):
#                 if method == "always":
#                     name = "msd_p_" + str(i) + "_insertion_always"
#                     m = "lsdpigeonhole -b " + str(i)
#                 elif method == "disabled":
#                     name = "msd_p_" + str(i) + "_insertion_disabled"
#                     m = "msdpigeonhole -b " + str(i)
#                 # elif method == 'ranges_doubled':
#                 #     name = 'msd_c_'+str(i)+"_insertion_ranges_doubled"
#                 #     m = 'msdpigeonhole -b ' + str(i)
#                 # else:
#                 #     name = 'msd_c_'+str(i)+"_insertion_ranges_copy"
#                 #     m = 'lsdpigeonhole -b ' + str(i)
#                 count = (
#                     10
#                     if ((method == "disabled" and i == 16) or method == "always")
#                     else 50
#                 )
#                 exc = (
#                     "/home/will/pypy2023/pypy_versions/"
#                     + name
#                     + '/bin/pypy sort_timer.py -es tiny small med -et "Few Unique" "Sorted" "Reverse Sorted" "Nearly Sorted" -em '
#                     + m
#                     + " -o "
#                     + fil
#                     + " -n "
#                     + str(count)
#                     + " -l "
#                     + str(l)
#                 )
#                 print("\033[1;35m")
#                 print(exc)
#                 print("")
#                 subprocess.run(exc, shell=True)


if __name__ == "__main__":
    output = get_filename("_".join(methods)) if len(methods) > 1 else get_filename(methods[0])
    for i in methods:
        # ins_ll(i, output)
        n(i, get_filename(i))
