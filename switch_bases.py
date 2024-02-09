import os
import re

radixsort_location = "/home/will/dissertation/radixsort_versions"

# Simplified regular expression
rg = re.compile(r"[_/.]")

def base_switch(version):
    filenames = get_files(os.path.join(radixsort_location, version, "originals"))
    cutoffs = [2000, 2000, 2500, 6400, 12000, 12000]
    cutoffs = ["self.threshold" for _ in cutoffs]
    use_cutoff = False
    for name in filenames:
        radix, integer = rg.split(name)[:2]
        data = read_file(os.path.join(radixsort_location, version, "originals", name))
        base_line = next(i for i, line in enumerate(data) if "self.base =" in line)
        if radix == "msd" and use_cutoff:
            cutoff_line = next(i for i, line in enumerate(data) if "(end - start) <" in line)
        for base in range(6, 18, 2):
            data[base_line] = f"            self.base = {base}\n"
            if radix == "msd" and use_cutoff:
                data[cutoff_line] = f"                    if (end - start) < {cutoffs[(base // 2) - 3]}:\n"
            output_filename = f"{radix}_{integer}_{base}.py"
            write_file(os.path.join(radixsort_location, version, output_filename), data)

def read_file(path):
    with open(path, "r") as file:
        return file.readlines()

def write_file(path, data):
    with open(path, "w") as file:
        file.writelines(data)

def get_files(path):
    return [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

if __name__ == "__main__":
    base_switch("always_insert_update")
    base_switch("never_insert_update")
