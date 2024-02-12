import os
import subprocess
from compile import *
import random
sort_times = "/home/will/dissertation/sort_times"
# methods = ["fewer_iters"]
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
        if ('c' not in name or '8' not in name ) or ('p' not in name or '8' not in name ):continue
        packagename = re.split(rg, name)[0] if methodName != "timsort" else "timsort"
        exepath = f'{pypy_versions}/{packagename}_{methodName}/bin/pypy'
        if not os.path.exists(exepath):continue
        for l in [100000]:
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

def ins(methodName, output, thresh=100, threshdivs=20, num=1):
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
        # if '12' not in name and '14' not in name and '16' not in name: continue
        if 'p_14' not in name: continue
        packagename = re.split(rg, name)[0] if methodName != "timsort" else "timsort"
        exepath = f'{pypy_versions}/{packagename}_{methodName}/bin/pypy'
        if not os.path.exists(exepath):continue
        for l in [1000000]:
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

def handler(methods):
    # output = get_filename("_".join(methods)) if len(methods) > 1 else get_filename(methods[0])
    for i in methods:
        ins(i, get_filename(i))
