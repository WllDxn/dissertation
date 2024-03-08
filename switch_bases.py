import os
import re

radixsort_location = "/home/will/dissertation/radixsort_versions"

# Simplified regular expression
rg = re.compile(r"[_/.]")

def base_switch(version, use_cutoff=True):
    filenames = get_files(os.path.join(radixsort_location, version, "originals"))
    cutoffs_c = [str(x) for x in [10, 22, 22, 40, 112, 275, 550, 1240]]
    cutoffs_p = [str(x) for x in [500, 350, 300, 300, 300, 450, 700, 1750]]
    # if use_thresh:
    # cutoffs = ["self.threshold" for _ in cutoffs]

    for name in filenames:
        radix, integer = rg.split(name)[:2]
        data = read_file(os.path.join(radixsort_location, version, "originals", name))
        base_line = next(i for i, line in enumerate(data) if "self.base =" in line)
        if radix == "msd" and use_cutoff:
           cutoff_line = next(i for i, line in enumerate(data) if "if (end - start) <" in line)
        for idx, base in enumerate(range(2, 18, 2)):
            data[base_line] = f"            self.base = {base}\n"
            if radix == "msd" and use_cutoff:
                data[cutoff_line] = f"                    if (end - start) < {cutoffs_c[idx] if 'c' in name else cutoffs_p[idx]}:\n"
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
import sys
if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(sys.argv[1])
        base_switch(sys.argv[1], True)
    else:
        print('give name')
#     # base_switch("never_insert_update")
