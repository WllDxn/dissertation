from contextlib import contextmanager
import itertools
import json
import time
import sys
import struct
import argparse
import os
import numpy as np

def genGraph(cols, max_value, type='random'):
    lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    #---Random List---
    if type=='random':
        random_list = lis[:]
        return random_list
    #---Few Unique---
    if type=='few_unique':
        few_unique = (np.random.choice(lis[0:len(lis) // 10], cols)).tolist()
        return few_unique
    #---Sorted List---
    lis.sort()
    sorted_list = lis[:]
    if type=='sorted':
        return sorted_list
    #---Reverse Sorted
    if type=='reverse_sorted':
        reverse_sorted = sorted_list[:]
        reverse_sorted.reverse()
        return reverse_sorted
    #---Nearly Sorted
    if type=='nearly_sorted':
        nearly_sorted = sorted_list[:]
        for _ in range(len(nearly_sorted) // 4):
            idx1 = np.random.randint(0, len(nearly_sorted) - 2)
            tmp = nearly_sorted[idx1]
            nearly_sorted[idx1] = nearly_sorted[idx1 + 1]
            nearly_sorted[idx1 + 1] = tmp
        return nearly_sorted
        
def myp(input):
    print(input, end='')
class Sorter:
    def __init__(self, config):
        self.outputpath = self.create_output_dictionary(config["output"])
        filepath = "%s/%s" % (
            str(os.path.dirname(os.path.realpath(__file__))),
            config["input"],
        )
        with open(filepath, "r") as f:
            self.data = json.load(f)
        self.time_start = time.time()
        self.timsort = config["timsort"]
        self.base_list = [0] if self.timsort else config["bases"]
        self.max_list_count = config["list_count"][0]
        self.max_list_length = config["list_length"]
        self.failed = {}
        self.unsorted = {}
        self.sorted = {}
        self.total_count = 0
        self.methods = self.include_methods(config["include_methods"])
        self.excluded_datasizes = config["exclude_data_sizes"]
        self.excluded_datatypes = config["exclude_data_types"]
        self.begin_sorting()

    def include_methods(self, methods):
        included = []
        if "msdpigeonhole" in methods:
            included.append(0)
        if "msdcount" in methods:
            included.append(1)
        if "lsdpigeonhole" in methods:
            included.append(2)
        if "lsdcount" in methods:
            included.append(3)
        return included

    def create_output_dictionary(self, output):
        if output:
            path = output[0]
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            path = "%s/sort_times.json" % (dir_path)
            uniq = 1
            while os.path.exists(path):
                path = "%s/sort_times_%d.json" % (dir_path, uniq)
                uniq += 1
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("{}")
        return path

    def begin_sorting(self):
        for list_length in self.max_list_length:
            myp( "\033[1;36mLength: "+str(list_length)+"\n")
            for x in range(len(self.data)):
                if (
                    self.data[x]["data_type"] in self.excluded_datatypes
                    or self.data[x]["data_size"] in self.excluded_datasizes
                ):
                    continue
                print(x)
                count = 1
                time_interval = time.time()
                with open(self.data[x]["key"], "rb") as f:
                    fileReader = self.intlist_generator(f)
                    count = 0
                    myp( "\033[?25l")
                    while True:
                        self.print_sortmethod_count(x, count)
                        curr_list = list(itertools.islice(fileReader, list_length))
                        if not curr_list:
                            break
                        for method_idx in range(1) if self.timsort else self.methods:
                            for base in self.base_list:
                                name = (
                                    "tim_sort_base0"
                                    if self.timsort
                                    else self.getMethod(method_idx) + str(base)
                                )
                                self.data[x]["times"].setdefault(name, [])
                                try:
                                    self.sort_list(x, curr_list, method_idx, base, name)
                                except Exception as error:
                                    self.append_results_dict(
                                        x, self.failed, method_idx, base, name, error
                                    )
                                myp(
                                    self.getMethod(
                                        count % 5 if self.timsort else method_idx,
                                        block=True,
                                    )
                                )
                            myp( "\b" * len(self.base_list))
                        count += 1
                        self.total_count += 1
                        if count == self.max_list_count:
                            break
                self.print_sortmethod_evaluation(time_interval, x)
                self.write_dict(x, list_length)
            self.print_conclusion(x)

    def append_results_dict(self, x, results_dict, method_idx, base, name, error=None):
        results_dict.setdefault(name, [])
        results_dict[name].append(
            (
                self.getMethod(method_idx),
                str(base),
                self.data[x]["data_size"],
                self.data[x]["data_type"],
                error,
            )
        )

    def is_unsorted(self, lst, print_unsorted=False, print_counts=False):
        s = None
        unsorted = []
        for base in range(len(lst) - 1):
            if lst[base] > lst[base + 1]:
                unsorted.append(base)
                s = False
        if s is False:
            s = len(unsorted)
            if print_counts:
                st1 = "unsorted %d out of %d" % (len(unsorted), len(lst))
                st2 = str([(lst[base], base) for base in unsorted][:100])
                myp(st1)
                myp(st2)
            if print_unsorted:
                method_idx = 0
                myp(len(unsorted))
                f = False
                for base in range(100):
                    if method_idx == len(unsorted) or base != unsorted[method_idx]:
                        col = "\033[1;32m"
                    else:
                        col = "\033[1;31m"
                        method_idx += 1
                        f = True
                    if f:
                        myp( col + str(lst[base]) + ",")
        return s

    def intlist_generator(self, f):
        while True:
            h = f.read(1024)
            m = struct.unpack(">%dq" % (len(h) // 8), h)
            if not m:
                break
            for x in m:
                yield x

    def getMethod(self, method_idk, block=False):
        if method_idk == 3:
            return "█" if block else "lsd_counting_sort_base"
        if method_idk == 2:
            return "▆" if block else "lsd_pigeonhole_sort_base"
        if method_idk == 1:
            return "▄" if block else "msd_counting_sort_base"
        if method_idk == 0:
            return "▂" if block else "msd_pigeonhole_sort_base"
        if method_idk == 4:
            return " "

    def write_dict(self, x, list_length):
        with open(self.outputpath, "r+") as f:
            new_dict = json.load(f)
            main_key = "radix_sort"
            new_dict.setdefault(main_key, [])
            found = False
            for idx, base in enumerate(new_dict[main_key]):
                if (
                    base["data_type"] == self.data[x]["data_type"]
                    and base["data_size"] == self.data[x]["data_size"]      
                ):
                    if "rows" in list(base.keys()):
                        if base["rows"] == list_length and base["cols"] == self.max_list_count:
                            for key in list(self.data[x]["times"].keys()):
                                new_dict[main_key][idx]["times"].setdefault(key, [])
                                new_dict[main_key][idx]["rows"] = list_length
                                new_dict[main_key][idx]["cols"] = self.max_list_count
                                new_dict[main_key][idx]["times"][key] += self.data[x]["times"][
                                    key
                                ]
                            found = True
                            break
            if not found:
                self.data[x]["rows"] = list_length
                self.data[x]["cols"] = self.max_list_count
                new_dict[main_key].append(self.data[x])
            f.seek(0)
            json.dump(new_dict, f)
            f.truncate()

    def sort_list(self, x, curr_list, method_idx, base, name):
        arr = curr_list[:]
        # arr[0] = arr[0] if self.timsort else base
        # arr[1] = arr[1] if self.timsort else method_idx
        t = time.time()
        arr.sort()
        newTime = time.time() - t
        if not self.is_unsorted(arr):
            self.append_results_dict(x, self.sorted, method_idx, base, name)
        elif (
            self.data[x]["data_size"] + self.data[x]["data_type"]
            not in self.unsorted[name]
        ):
            self.append_results_dict(
                x,
                self.failed,
                method_idx,
                base,
                name,
            )
        self.data[x]["times"][name].append(newTime)
        del arr

    def print_sortmethod_count(self, x, count):
        datatabs = "\t" *  (4 - (len(self.data[x]["data_type"] + str(self.data[x]["data_size"])) // 15))
        counttabs = "\t" * (2 - len(str(count)+"/"+str(self.max_list_count)) //7)
        if not self.timsort: myp( "\033[K")
        myp(
            "\033[1;31m\r%s %s%sCurrent: %d/%d%s%d/%d\r\t\t\t"%(self.data[x]["data_type"],self.data[x]["data_size"],datatabs,(count),(self.max_list_count),counttabs,(self.total_count),(self.max_list_count * len(self.data)))

        )

    def print_sortmethod_evaluation(self, tdelta, x):
        name = "%s-%s" % (self.data[x]["data_type"], self.data[x]["data_size"])
        tabs = "\t\t" if len(name) < 16 else "\t"
        myp(
            "\033[1;32m\r\033[K%s%stime: %f s"%(name, tabs, (time.time() - tdelta))
            
        )
        if self.unsorted:
            myp( " unsorted: %d" % len(self.unsorted))
        if self.failed:
            myp( " fails: %d" % len(self.failed))
        myp( "\n")

    def print_conclusion(self, x):
        myp( "\r\033[K\033[1;35mTotal \t\t\ttime: %f s\n" % (time.time() - self.time_start))
        if self.failed:
            myp( "fails %s\n" % self.failed)
        if self.unsorted:
            myp( "\033[1;31m\nunsorted - \033[1;32m sorted \n")
            for key, value_ in self.unsorted.items():
                value_.sort()
                self.sorted[key].sort()
                myp("%s\n\033[1;31m%s\033[1;32m%s" % (key,str(self.unsorted[key]),str(len(self.sorted[key]))))
        myp(("\033[1;34mSaved to: %s\n"%self.outputpath ))
        myp( "\033[?25h")


def integer_range(minimum, maximum):
    def integer_range_checker(arg):
        try:
            i = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError("Must be an integer")
        if i < minimum or i > maximum:
            raise argparse.ArgumentTypeError(
                "Must be in range [%d .. %d]" % str(minimum), str(maximum)
            )
        return i

    return integer_range_checker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Employs sorting algorithms from the pypy executable this script was run by to sort lists and store the time results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="pypy handler.py",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="binaryDictionary.json",
        nargs=1,
        help="input json file generated by gendata.py",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        nargs=1,
        help="output json file to write times to. If none specified, one will be created",
    )
    parser.add_argument(
        "-b",
        "--bases",
        type=int,
        default=[4, 6, 8, 10, 12, 14, 16],
        nargs="*",
        help="bases to use for sorting.",
    )
    parser.add_argument(
        "-l",
        "--list-length",
        type=int,
        default=[1000000,100000,10000],
        nargs="*",
        help="Maximum number of ints to be read into each list",
    )
    parser.add_argument(
        "-n",
        "--list-count",
        type=integer_range(1, 1000000),
        default=[100],
        nargs=1,
        help="Maximum number of lists to be read and sorted",
    )
    parser.add_argument(
        "-t",
        "--timsort",
        default=False,
        action="store_true",
        help="use Timsort instead of Radix sort when sorting (Must use correct pypy version)",
    )
    methodchoices = ["lsdcount", "lsdpigeonhole", "msdcount", "msdpigeonhole"]
    parser.add_argument(
        "-em",
        "--include-methods",
        default=[],
        nargs="*",
        choices=methodchoices,
        help="Exclude methods while sorting, choose from: " + ", ".join(methodchoices),
        metavar=" ",
    )
    datasizechoices = ["tiny", "small", "med", "large"]
    parser.add_argument(
        "-es",
        "--exclude-data-sizes",
        default=[],
        nargs="*",
        choices=datasizechoices,
        help="Exclude Data sizes while sorting, choose from: "
        + ", ".join(datasizechoices),
        metavar=" ",
    )
    datachoices = ["Random", "Few Unique", "Sorted", "Reverse Sorted", "Nearly Sorted"]
    parser.add_argument(
        "-et",
        "--exclude-data-types",
        nargs="*",
        default=[],
        choices=datachoices,
        help="Exclude Data types while sorting, choose from: " + ", ".join(datachoices),
        metavar=" ",
    )
    args = parser.parse_args()
    sorter = Sorter(vars(args))
