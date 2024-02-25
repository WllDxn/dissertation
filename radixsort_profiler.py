import sys
from math import ceil, log, pow

from matplotlib.colors import rgb2hex
from minor_files.print_bits import print_arr
import numpy as np


import sys
from math import ceil, log, pow


def int_bytes(i, radix):
    """
    Retrieves the minimum number of bytes required to identify an integer.

    :param radix: Number base
    :param i: Input integer
    :return: Number of bytes used to identify integer
    """

    return int(ceil(log(absolute(i)) / log(radix))) + 1


def absolute(num):
    """
    Custom implementation of abs(Num)
    :param num: Number to find absolute value of
    :return: absolute value of num
    """
    if num == (-sys.maxsize) - 1:
        return sys.maxsize
    return -num if num < 0 else num


def make_radixsort_class(
    setitem=None,
    setslice=None,
):
    if setitem is None:

        def setitem(list, item, value):
            list[item] = value

    if setslice is None:

        def setslice(list, slice, index):
            list[index : index + len(slice)] = slice

    class Radixsort(object):
        def __init__(self, list, listlength=None):
            self.list = list
            self.base = 8
            self.listlength = len(self.list)
            self.radix = int(pow(2, self.base))
            self.threshold = self.list[0]

        def list_abs_max(self, checkorder=False):
            """
            Returns the list item that will require the most bits to express. (the smallest or the largest value)
            Also optinoally returns booleans stating whether the list is ordered or reverse ordered
            :param checkorder: Flag that determines whether to check whether the list is ordered
            :return: the maximum absolute value in the list
            """

            assert len(self.list) != 0
            m = self.list[0]
            n = self.list[0]
            prev = self.list[0]
            (ordered, reverseordered) = (True, True)
            for i in range(1, len(self.list)):
                if self.list[i] > m:
                    m = self.list[i]
                if self.list[i] < n:
                    n = self.list[i]
                if checkorder:
                    ordered &= self.list[i] >= prev
                    reverseordered &= self.list[i] <= prev
                    prev = self.list[i]
            if checkorder:
                self.ordered = ordered
                self.reverseOrdered = reverseordered
            return m if absolute(m) > absolute(n) else n

        def setitem(self, item, value):
            setitem(self.list, item, value)

        def setslice(self, slice, index):
            setslice(self.list, slice, index)
        @profile
        def insertion_sort(self, start, end):
            for step in range(start, end):
                key = self.list[step]
                j = step - 1
                while j >= 0 and key < self.list[j]:
                    self.setitem(j + 1, self.list[j])
                    j = j - 1
                self.setitem(j + 1, key)

        def reverseSlice(self, start=0, stop=0):
            if stop == 0:
                stop = self.listlength - 1
            while start < stop:
                i = self.list[start]
                j = self.list[stop]
                self.setitem(start, j)
                self.setitem(stop, i)
                start += 1
                stop -= 1

        def is_sorted(self, start=0, end=-1):
            end = end if end > -1 else self.listlength
            assert start >= 0
            assert end >= 0
            sortd, rsortd = True, True
            for i, el in enumerate(self.list[start + 1 : end]):
                # if i+start==end:break
                if el < self.list[start + i]:
                    sortd = False
                    if rsortd == False:
                        return sortd, rsortd
                if el > self.list[start + i]:
                    rsortd = False
                    if sortd == False:
                        return sortd, rsortd
            return sortd, rsortd
        @profile
        def sort(self):
            if self.listlength < 2:
                return
            if self.listlength < 2:
                return
            for step in range(0, self.listlength):
                key = self.list[step]
                j = step - 1
                while j >= 0 and key < self.list[j]:
                    self.setitem(j + 1, self.list[j])
                    j = j - 1
                self.setitem(j + 1, key)

    return Radixsort





import copy

if True:

    # print(str(i), end='  ')
    max_value = int(pow(2, 63))
    cols = 10000
    lis = np.random.randint(0, max_value, cols, dtype=np.int64).tolist()

    # lis2.append(int(pow(2, 63))-1)
    # lisf = copy.deepcopy(lis)
    r = make_radixsort_class()
    # r2 = make_radixsort_class_r()
    # rf = make_radixsort_class_o()
    # rf(lisf).sort()

    r(lis).sort()
    # r2(lis2).sort()
    # print
    print(
        "shifting sorted: "
        + str(all(lis[i] <= lis[i + 1] for i in range(len(lis) - 1)))
    )

    # def is_sorted(arr, key=lambda x: x):
    #     s = []
    #     print(str(arr[0]))
    #     for i, el in enumerate(arr[1:]):
    #         space = '' if el<0 else ' '
    #         if key(el) < key(arr[i]): # i is the index of the previous element
    #             print((space+"\033[1;31m"+str(el) + '\t'+space + hex(el)))
    #         else:
    #              print((space+"\033[1;32m"+str(el) + '\t' +space+ hex(el)))
    # is_sorted(lis)
    # print(("\033[1;0m"))


    # print('fixed    sorted: ' + str(all(lisf[i] <= lisf[i+1] for i in range(len(lisf) - 1))))

