from pathlib import Path
import itertools
import json
import time
import argparse
import numpy as np
import random
import tempfile
import os
import copy
methodchoices = ["lsdcount", "lsdpigeonhole", "msdcount", "msdpigeonhole"]
datasizechoices = ["tiny", "small", "med", "large"]
datachoices = ["Nearly Sorted", "Random", "Few Unique", "Sorted", "Reverse Sorted"]


def get_max_value(data_size):
    return {
        "large": 9223372036854775807,
        "med": 4294967296,
        "small": 1048576,
        "tiny": 65536,
    }.get(data_size, 65536)

def gen_list(cols, data_size, type="Random", threshold=None, insert=False, basemax=False):
    max_value = get_max_value(data_size) if basemax==False else int(pow(2,data_size))
    lis = []
    if type == "Random" and not insert:
        lis = np.random.randint(-max_value-1, max_value, cols, dtype=np.int64).tolist()
    elif insert:
        lis = [int(x) for x in range(-cols//2, cols//2+1)][:cols]
        if insert:
            random.shuffle(lis)
    elif type == "Few Unique":
        lis = np.random.randint(-max_value-1, max_value, cols, dtype=np.int64).tolist()
        lis = np.random.choice(lis[: len(lis) // 10], cols).tolist()
    elif type == "Sorted" or insert:
        lis = [int(x*(max_value/cols)) for x in list(range(-cols//2,(cols//2)+1, 1))][:cols]
        # lis = [int(x) for x in range(-max_value-1, max_value, int((2*max_value)/cols))]
    elif type == "Reverse Sorted":
        lis = [int(x*(max_value/cols)) for x in list(range(cols//2,(-cols//2)-1, -1))][:cols]
        # lis = [int(x) for x in range(max_value, -max_value-1, int(-(2*max_value)/cols))]
    elif type == "Nearly Sorted":
        # lis = [int(x) for x in range(-max_value-1, max_value, int((2*max_value)/cols))]
        lis = np.random.randint(-max_value-1, max_value, cols, dtype=np.int64).tolist()
        lis.sort()
        for idx1 in range(len(lis) - 2):
            if random.random() < 0.1:
                lis[idx1], lis[idx1 + 1] = lis[idx1 + 1], lis[idx1]
        # print(lis[:10])
    lis[0] = threshold if threshold is not None else lis[0]
    return [int(x) for x in lis]
import sys

def myp(input):

    print(input, end=",\n")
    sys.stdout.flush()


class Sorter:
    def __init__(self, config):
        self.outputpath = self.create_output_dictionary(config["output"])
        self.time_start = time.time()
        self.max_list_count = config["list_count"]
        self.max_list_length = config["list_length"] 
        self.insert = config["insert"]
        self.threshold = config["threshold"][0]
        self.threshold_divisions = config["thresholddivs"][0]
        self.total_count = 0
        self.method = config["method"][0]
        self.datasizes = [
            item for item in datasizechoices if item not in config["exclude_data_sizes"]
        ]
        self.datatypes = [
            item for item in datachoices if item not in config["exclude_data_types"]
        ]
        self.basemax = config["basemax"]
        self.begin_sorting()

    def create_output_dictionary(self, output):
        # sourcery skip: replace-interpolation-with-fstring
        if output:
            path = output[0]
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__).join('sort_times'))
            with tempfile.NamedTemporaryFile(dir=dir_path, prefix="sort_times_", suffix=".json", delete=False) as tmp_file:
                path = tmp_file.name
        return path

    def set_data(self, data, list_length, data_size, data_type, time, threshold=None):
        for entry in data["radix_sort"]:
            if (
                entry["data_type"] == data_type
                and entry["data_size"] == data_size
                and entry["rows"] == self.max_list_count
                and entry["cols"] == list_length
                and (threshold is None or threshold == entry["threshold"])
            ):
                entry["times"].setdefault(self.method, []).append(time)
                return data
        new_entry = {
            "data_type": data_type,
            "data_size": data_size,
            "rows": self.max_list_count,
            "cols": list_length,
            "times": {self.method: [time]},
        }
        if threshold is not None:
            new_entry["threshold"] = threshold
        data["radix_sort"].append(new_entry)
        return data

    def begin_sorting(self):
        for i in range(50):
            curr_list = gen_list(10000, "med", "Random", None)
            # myp("warming,%d,100" % (i + 1))
        if not os.path.exists(self.outputpath):
            data = {"radix_sort": []}
        else:
            with open(self.outputpath, "r+") as f:
                data = json.load(f)
                data.setdefault("radix_sort", [])
        
        def generate_items():
            for list_length in self.max_list_length if not self.insert else list(range(max(1,(self.max_list_length[0]+1)//50), self.max_list_length[0]+1, max(1, (self.max_list_length[0]+1)//50))):
                for data_size in self.datasizes if not self.basemax else list(range(0, self.basemax+1, 2)):
                    for data_type in self.datatypes:
                        thresholds = [None] if self.threshold is None else range(0, self.threshold + 1, self.threshold // self.threshold_divisions)
                        for threshold in thresholds:
                                yield list_length, data_size, data_type, threshold
        
        items = generate_items()
        items = list(items)
        # randlists = [gen_list(self.max_list_length[0], self.datasizes[0], self.datatypes[0], 0) for _ in range(self.max_list_count)]
        # if self.threshold is not None:
        
        interval = 0
        sortd=True
        for (list_length, data_size, data_type, threshold), count in list(itertools.product(items, range(self.max_list_count))):
            self.print_sortmethod_count(data_size, data_type, count, len(items)*self.max_list_count)
            # curr_list = list(randlists[count])
            curr_list = gen_list(list_length, data_size, data_type, threshold, self.insert)
            if threshold:
                curr_list[0]=threshold
            
            t1_start = time.perf_counter()
            curr_list.sort()
            t1_stop = time.perf_counter()
            sortd &= all(curr_list[i] <= curr_list[i+1] for i in range(len(curr_list) - 1))
            del curr_list
            newtime = t1_stop - t1_start
            data = self.set_data(data, list_length, data_size, data_type, newtime, threshold)
            interval += newtime
            if count + 1 == self.max_list_count:
                self.print_sortmethod_evaluation(interval, data_type, data_size, list_length, True, threshold)
                interval = 0
            self.total_count += 1
        with open(self.outputpath, "w+") as f:
            json.dump(data, f, indent=4)
        self.print_conclusion()


    def print_sortmethod_count(
        self, data_size, data_type, count, total_items
    ):
        tabs = "\t\t" if len(f'Current: {count}/{self.max_list_count}') < 16 else "\t"
        myp(
            f"count,{data_type},{data_size},{count},{self.max_list_count},{self.total_count},{total_items}"
        )

    def print_sortmethod_evaluation(
        self, tdelta, data_type, data_size, list_length, sortd, threshold=None
    ):
        name = "%s,%s" % (data_type, data_size)
        ll = list(range(max(1,(self.max_list_length[0]+1)//50), self.max_list_length[0]+1, max(1,(self.max_list_length[0]+1)//50))) if self.insert else [self.max_list_length]
        myp(
            "eval,%s,%f,%d,%s,%s"
            % (name, tdelta, list_length, str(sortd), (str(len(ll))))
        )
        if threshold is not None:
            myp(",%d" % threshold)

    def print_conclusion(self):
        myp(
            "Total,%f\n"
            % (time.time() - self.time_start)
        )


def integer_range(minimum, maximum):
    def integer_range_checker(arg):
        i = int(arg)
        if i < minimum or i > maximum:
            raise argparse.ArgumentTypeError(f"Must be in range [{minimum} .. {maximum}]")
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
        "-l",
        "--list-length",
        type=int,
        default=[10000, 100000, 1000000],
        nargs="*",
        help="Maximum number of ints to be read into each list",
    )
    parser.add_argument(
        "-n",
        "--list-count",
        type=integer_range(1, 1000000),
        default=100,
        help="Maximum number of lists to be read and sorted",
    )
    parser.add_argument(
        "-m",
        "--method",
        type=str,
        nargs=1,
        help="Name of method used for sorting",
    )
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
    parser.add_argument(
        "-et",
        "--exclude-data-types",
        nargs="*",
        default=[],
        choices=datachoices,
        help="Exclude Data types while sorting, choose from: " + ", ".join(datachoices),
        metavar=" ",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        nargs="*",
        default=[None],
        help="Maximum threshold",
    )
    parser.add_argument(
        "-d",
        "--thresholddivs",
        type=int,
        nargs="*",
        default=[None],
        help="Maximum threshold divisions",
    )
    parser.add_argument(
        "-s",
        "--insert",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Use insertion test feature"
    )
    parser.add_argument(
        "-b",
        "--basemax",
        type=integer_range(1,64),
        nargs="?",
        default=None,
        help="Perform testing of lists of all sizes up to and including 2 to the power of the given basse (override -es)"
    )
    
    args = parser.parse_args()
    sorter = Sorter(vars(args))
