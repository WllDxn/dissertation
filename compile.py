import os
import re
import subprocess

radixsort_location = "/home/will/dissertation/radixsort_versions"
pypy_src_location = "/home/will/dissertation/pypy_misc/pypy3.10-v7.3.15-src"
pypy_versions = "/home/will/dissertation/pypy_versions"


def compile(version):
    filenames = get_files(f"{radixsort_location}/{version}")
    existingnames = list(get_directories(f"{pypy_versions}"))
    cg = "\/tmp([^']*)"
    rg = "[/.+?\./]"
    for name in filenames:
        packagename = f"{re.split(rg, name)[0]}_{version}"
        if packagename in existingnames:
            print(f'skipping: {str(name)}')
            continue
        cmd_str = f"cp {radixsort_location}/{version}/{name} {pypy_src_location}/rpython/rlib/radixsort.py"
        subprocess.run(cmd_str, shell=True)
        print(
            f"---------------------------{packagename}------------------------------------------"
        )
        cmd_str = "pypy ../../rpython/bin/rpython --opt=jit"
        subprocess.run(cmd_str, shell=True, cwd=f"{pypy_src_location}/pypy/goal")
        cmd_str = f"pypy ../tool/release/package.py --archive-name=pypy-{packagename} --without-_ssl"
        result = subprocess.check_output(
            cmd_str, shell=True, cwd=f"{pypy_src_location}/pypy/goal"
        )
        temp = result.decode("utf-8").strip()
        test = re.findall(cg, temp)[0]
        cmd_str = f"cp -r /tmp{test}/pypy-{packagename} {pypy_versions}/{packagename}"
        subprocess.run(cmd_str, shell=True, cwd=f"{pypy_src_location}/pypy/goal")
        exc = f"{pypy_versions}/{packagename}/bin/pypy -m ensurepip"
        subprocess.run(exc, shell=True)
        exc = f"{pypy_versions}/{packagename}/bin/pypy -mpip install numpy"
        subprocess.run(exc, shell=True)
        cmd_str = f"cp {pypy_src_location}/rpython/rlib/radixsort.py {pypy_versions}/{packagename}/{name}"
        subprocess.run(cmd_str, shell=True)


def get_directories(path):
    for file in os.listdir(path):
        if not os.path.isfile(os.path.join(path, file)):
            yield file
def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


if __name__ == "__main__":
    compile("only_insert")
    # compile("always_insert")
    # compile("never_insert")
    # compile("insertion_tests_3")
