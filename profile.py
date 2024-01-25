from math import ceil, log, pow
import sys
import numpy as np

def int_bytes(i, radix):
    """
    Retrieves the minimum number of bytes required to identify an integer.

    :param radix: Number base
    :param i: Input integer
    :return: Number of bytes used to identify integer
    """

    return int(ceil(log(absolute(i))/  log(radix))) + 1


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
        def setslice(self, slice, index):
            setslice(self.list,slice,index)
    class Radixsort(object):
        def __init__(self, list, listlength=None):
            self.list = list
            self.base = 0
            self.listlength = len(self.list)
            self.radix = 0

        def setitem(self, item, value):
            setitem(self.list, item, value)
        def setslice(self, slice, index):
            setslice(self.list,slice,index)
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
        @profile
        def setbase(self, listmax):
            prev = 4
            select = 0
            for i in range(16, 4, -2):
                val = ceil(int_bytes(listmax, 2) / i)
                if val <= prev:
                    prev = val
                    select = i
                else:
                    break
            self.base = select
            self.radix = int(pow(2, select))
            return
        @profile
        def sort(self):
            if self.listlength < 2:
                return
            listmax = self.list_abs_max(checkorder=True)
            self.setbase(listmax)
            # print(self.base)
            min_bytes = int_bytes(listmax, self.radix)
            if self.ordered == True:
                return
            if self.reverseOrdered == True:
                self.reverseSlice()
                return
            if min_bytes == int_bytes((-sys.maxsize) - 1, self.radix):
                uint_63 = uint_63 = ~((1 << int_bytes(listmax, 2) - 1) - 1)
                min_bytes -= 1
                ovf = True
            else:
                uint_63 = ~((1 << int_bytes(listmax, 2)) - 1)
                ovf = False
            disc = 0
            bucket = [[] for _ in range(self.radix)]
            for i in range(min_bytes + 1):
                shift = (self.base) * i
                for num in self.list:
                    sortkey = (num & ~disc) ^ uint_63
                    val = (sortkey >> shift) & self.radix - 1
                    bucket[val].append(num)
                if (bucket.count([])) == len(bucket)-1:
                    continue
                index = 0
                for bdx, b in enumerate(bucket):
                    self.setslice(b, index)
                    index+=len(b)
                    bucket[bdx] = []
                disc = (
                        ((1 << shift) - 1)
                        if (not ovf) or i < min_bytes 
                        else ((1 << (shift - self.base)) - 1)
                    )

    return Radixsort

import copy
for i in range(7,64,8):  
    # print(str(i), end='  ')  
    max_value = int(pow(2,i))
    cols = 100000
    lis = np.random.randint(0, max_value, cols, dtype=np.int64).tolist()
    # lisf = copy.deepcopy(lis)
    r = make_radixsort_class()
    # rf = make_radixsort_class_f()
    r(lis).sort()
    # rf(lisf).sortf()
    print('shifting sorted: ' + str(all(lis[i] <= lis[i+1] for i in range(len(lis) - 1))))
    # print('fixed    sorted: ' + str(all(lisf[i] <= lisf[i+1] for i in range(len(lisf) - 1))))