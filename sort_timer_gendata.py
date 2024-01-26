from pathlib import Path
import itertools
import json
import time
import argparse
import numpy as np
import random
import tempfile

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

def gen_list(cols, data_size, type="Random", threshold=None):
    max_value = get_max_value(data_size)
    lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    lis[0] = threshold if threshold is not None else lis[0]

    if type == "Random":
        return lis
    elif type == "Few Unique":
        return np.random.choice(lis[: len(lis) // 10], cols).tolist()
    elif type == "Sorted":
        lis.sort()
        return lis
    elif type == "Reverse Sorted":
        lis.reverse()
        return lis
    elif type == "Nearly Sorted":
        for idx1 in range(len(lis) - 2):
            if random.random() < 0.1:
                lis[idx1], lis[idx1 + 1] = lis[idx1 + 1], lis[idx1]
        return lis


def myp(input):
    print(input, end="")


class Sorter:
    def __init__(self, config):
        self.outputpath = self.create_output_dictionary(config["output"])
        self.time_start = time.time()
        self.max_list_count = config["list_count"][0]
        self.max_list_length = config["list_length"]
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
        self.begin_sorting()

    def create_output_dictionary(self):
        with tempfile.NamedTemporaryFile(
            delete=False,
            dir=Path.cwd(),
            prefix=f"{__file__}.sort_times_",
            suffix=".json",
        ) as tf:
            return tf.name

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
                return
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

    def begin_sorting(self):
        for i in range(100):
            curr_list = gen_list(10000, "med", "Random", None)
            myp("\033[1;36m\r\033[KWarming up: %d/100" % (i + 1))
        print("")
        with open(self.outputpath, "r+") as f:
            data = json.load(f)
            data.setdefault("radix_sort", [])
        
        def generate_items():
            for list_length in self.max_list_length:
                for data_size in self.datasizes:
                    for data_type in self.datatypes:
                        thresholds = [None] if self.threshold is None else range(0, self.threshold + 1, self.threshold // self.threshold_divisions)
                        for threshold in thresholds:
                            for count in range(self.max_list_count):
                                yield list_length, data_size, data_type, threshold, count
        
        items = generate_items()
        if self.threshold is not None:
            items = list(items)
            random.shuffle(items)
        
        interval = time.time()
        for list_length, data_size, data_type, threshold, count in items:
            self.print_sortmethod_count(data_size, data_type, count, len(items), interval)
            curr_list = gen_list(list_length, data_size, data_type, threshold)
            t1_start = time.perf_counter()
            curr_list.sort()
            t1_stop = time.perf_counter()
            newtime = t1_stop - t1_start
            data = self.set_data(data, list_length, data_size, data_type, newtime, threshold)
            if count + 1 == self.max_list_count and threshold is not None:
                self.print_sortmethod_evaluation(interval, data_type, data_size, list_length, True, threshold)
                interval = time.time()
            self.total_count += 1
        with open(self.outputpath, "w") as f:
            json.dump(data, f)
        self.print_conclusion()


    def print_sortmethod_count(
        self, data_size, data_type, count, total_items, interval
    ):
        myp(
            f"\033[K\033[1;31m\r{data_type} {data_size}\tCurrent: {count}/{self.max_list_count}\t{self.total_count}/{total_items}\ttime: {time.time()-interval} s"
        )

    def print_sortmethod_evaluation(
        self, tdelta, data_type, data_size, list_length, sortd, threshold=None
    ):
        name = "%s-%s" % (data_type, data_size)
        tabs = "\t\t" if len(name) < 16 else "\t"
        myp(
            "\033[1;32m\r\033[K%s%stime: %f s  data size: %d  Sorted: %s"
            % (name, tabs, (time.time() - tdelta), list_length, str(sortd))
        )
        if threshold is not None:
            myp("  Threshold: %d" % threshold)
        myp("\n")

    def print_conclusion(self):
        myp(
            "\r\033[K\033[1;35mTotal \t\t\ttime: %f s\n"
            % (time.time() - self.time_start)
        )
        myp(("\033[1;34mSaved to: %s\n" % self.outputpath))
        myp("\033[?25h")


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
    args = parser.parse_args()
    sorter = Sorter(vars(args))
