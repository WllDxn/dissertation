import os
import re

radixsort_location = "/home/will/dissertation/radixsort_versions"
pypy_src_location = "/home/will/dissertation/pypy_versions/pypy3.10-v7.3.15-src"
pypy_versions = "/home/will/dissertation/pypy_versions"

# Precompile the regular expression
rg = re.compile(r"[/.+?\./]")


def base_switch(version):
    filenames = get_files(os.path.join(radixsort_location, version, "originals"))
    cutoffs = [2000, 2000, 2500, 6400, 12000, 12000]
    for name in filenames:
        radix, integer = rg.split(name)[0].split("_")
        fn = os.path.join(radixsort_location, version, "originals", name)
        with open(fn, "r") as file:
            data = file.readlines()
        k = 0
        while "self.base =" not in data[k]:
            k += 1
        mk = 0
        if radix == "msd":
            while "if (end - start) <" not in data[mk]:
                mk += 1
        for base in range(6, 18, 2):
            base_str = str(base)
            data[k] = f"            self.base = {base_str}\n"
            if radix == "msd":
                cutoff_str = str(cutoffs[(base // 2) - 3])
                data[mk] = f"                    if (end - start) < {cutoff_str}:\n"
            output_filename = f"{radix}_{integer}_{base_str}.py"
            output_path = os.path.join(radixsort_location, version, output_filename)
            with open(output_path, "w") as file:
                file.writelines(data)


def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


if __name__ == "__main__":
    base_switch("isolate_byte")
