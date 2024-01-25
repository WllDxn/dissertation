from contextlib import contextmanager
import itertools
import json
import time
import sys
import struct
import argparse
import os
import numpy as np
import random
methodchoices = ["lsdcount", "lsdpigeonhole", "msdcount", "msdpigeonhole"]
datasizechoices = ["tiny", "small", "med", "large" ]
datachoices = ["Nearly Sorted", "Random", "Few Unique", "Sorted", "Reverse Sorted"]

def gen_list(cols, data_size, type='random'):
    max_value = {'large':9223372036854775807, 'med':4294967296, 'small': 1048576, 'tiny': 65536}[data_size]
    lis = np.random.randint(-max_value, max_value, cols, dtype=np.int64).tolist()
    #---Random List---
    if type=='Random':
        return lis
    #---Few Unique---
    if type=='Few Unique':
        few_unique = (np.random.choice(lis[0:len(lis) // 10], cols)).tolist()
        return few_unique
    #---Sorted List---
    lis.sort()
    if type=='Sorted':
        return lis
    #---Reverse Sorted
    if type=='Reverse Sorted':
        lis.reverse()
        return lis
    #---Nearly Sorted
    if type=='Nearly Sorted':
        for idx1 in range(len(lis) - 2):
            if random.random() < 0.1:
                tmp = lis[idx1]
                lis[idx1] = lis[idx1 + 1]
                lis[idx1 + 1] = tmp
        return lis
        
def myp(input):
    print(input, end='')
class Sorter:
    def __init__(self, config):
        self.outputpath = self.create_output_dictionary(config["output"])
        self.time_start = time.time()
        self.max_list_count = config["list_count"][0]
        self.max_list_length = config["list_length"]
        self.thresholds = list(range(config["threshold"][0],config["threshold"][1],(config["threshold"][1]-config["threshold"][0])//100))
        self.total_count = 0
        self.method = config["method"][0]
        self.datasizes = [item for item in datasizechoices if item not in config["exclude_data_sizes"]]
        self.datatypes = [item for item in datachoices if item not in config["exclude_data_types"]]
        self.begin_sorting()

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

    def set_data(self, data, list_length, data_size, data_type, time, threshold):
        dict = data['radix_sort']
        for idx, i in enumerate(dict):
            if i['data_type'] == data_type and i['data_size'] == data_size and i['rows'] == self.max_list_count and i['cols'] == list_length and i['threshold'] == threshold:
                data['radix_sort'][idx]['times'].setdefault(self.method,[])
                data['radix_sort'][idx]['times'][self.method].append(time)
                return data
        newData = {}
        newData.setdefault("data_type", data_type)
        newData.setdefault("data_size", data_size)
        newData.setdefault("rows", self.max_list_count)
        newData.setdefault("cols", list_length)
        newData.setdefault("threshold", threshold)
        newData.setdefault("times", {})
        newData['times'].setdefault(self.method,[])
        newData['times'][self.method].append(time)
        data['radix_sort'].append(newData)
        return data
            
  
        
    def begin_sorting(self):
        for i in range(1000):
            myp("\033[K\033[1;36m\rWarming up: %d/1000"%(i+1,))
            temp=gen_list(10000, "large", "Random")
            temp[0]=200
            temp.sort()
        print("")
        with open(self.outputpath, "r+") as f:
            data = json.load(f)
            data.setdefault("radix_sort", [])

        items = list(itertools.product(self.max_list_length, self.datasizes, self.datatypes, self.thresholds, list(range(self.max_list_count))))
        interval = time.time()
        for list_length, data_size, data_type, count, threshold in items:
            self.print_sortmethod_count(data_size, data_type, count, len(items),interval)           
            curr_list = gen_list(list_length, data_size, data_type)
            curr_list[0] = threshold
            t1_start = time.perf_counter() 
            curr_list.sort()
            t1_stop = time.perf_counter()
            newtime = t1_stop-t1_start
            data = self.set_data(data, list_length, data_size, data_type, newtime, threshold)
            if count+1 == self.max_list_count:
                self.print_sortmethod_evaluation(interval, data_type, data_size, list_length)
                interval = time.time()
            self.total_count+=1
        with open(self.outputpath, "r+") as f:
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        self.print_conclusion()

    


    def print_sortmethod_count(self, data_size, data_type, count, total_items, interval):
        datatabs = "\t" *  (4 - (len(data_type + str(data_size)) // 15))
        counttabs = "\t" * (2 - len(str(count)+"/"+str(self.max_list_count)) //7)
        myp( "\033[K")
        myp(
            "\033[1;31m\r%s %s%s   Current: %d/%d%s%d/%d\r\t\t\t"%(data_type,data_size,datatabs,(count),(self.max_list_count),counttabs,(self.total_count),(total_items))

        )
        myp("time: %f s"%(time.time()-interval))

    def print_sortmethod_evaluation(self, tdelta, data_type, data_size, list_length):
        name = "%s-%s" % (data_type, data_size)
        tabs = "\t\t" if len(name) < 16 else "\t"
        myp(
            "\033[1;32m\r\033[K%s%stime: %f s  data size: %d"%(name, tabs, (time.time() - tdelta), list_length)
            
        )
        myp( "\n")

    def print_conclusion(self):
        myp( "\r\033[K\033[1;35mTotal \t\t\ttime: %f s\n" % (time.time() - self.time_start))
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
        "-l",
        "--list-length",
        type=int,
        default=[10000,100000,1000000],
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
        "-m",
        "--method",
        type=str,
        nargs = 1,
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
        default=[0,1000],
        nargs=2,
        help="input threshold range",
    )
    args = parser.parse_args()
    sorter = Sorter(vars(args))
