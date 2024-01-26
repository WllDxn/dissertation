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

        def setslice(list, slice, index):
            list[index : index + len(slice)] = slice

    class Radixsort(object):
        def __init__(self, list, listlength=None):
            self.list = list
            self.base = 8
            self.listlength = len(self.list)
            self.radix = int(pow(2, self.base))
            self.threshold = self.list[0]

        def setitem(self, item, value):
            setitem(self.list, item, value)

        def setslice(self, slice, index=0):
            setslice(self.list, slice, index)

        def list_abs_max(self, checkorder=False):
            assert len(self.list) != 0
            m = max(self.list, key=absolute)
            if checkorder:
                self.ordered = all(self.list[i] >= self.list[i - 1] for i in range(1, len(self.list)))
                self.reverseOrdered = all(self.list[i] <= self.list[i - 1] for i in range(1, len(self.list)))
            return m


        def insertion_sort(self, start, end):
            for step in range(start, end):
                key = self.list[step]
                j = step - 1
                while j >= 0 and key < self.list[j]:
                    self.setitem(j + 1, self.list[j])
                    j = j - 1
                self.setitem(j + 1, key)


        def reverseSlice(self, start=0, stop=None):
            if stop is None:
                stop = self.listlength
            self.list[start:stop] = self.list[start:stop][::-1]



        def sort(self):
            if self.listlength < 2:
                return
            listmax = self.list_abs_max(checkorder=True)
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
            count = [0 for _ in range(self.radix)]
            bucket_indexes = [(0, self.listlength)]
            temp_list = self.list[:]
            disc = 0
            shift = min_bytes * self.base
            disc = ((1 << shift + self.base) - 1) if (not ovf) else ((1 << (shift)) - 1)
            for k in range(min_bytes - 1, -1, -1):
                shift = k * self.base
                temp_bucket_indexes = []
                for start, end in bucket_indexes:
                    if start + 1 == end:
                        continue
                    if (end - start) < self.threshold: 
                        self.insertion_sort(start, end)
                        for i in range(start, end):
                            temp_list[i] = self.list[i]
                        continue
                    for idx in range(start, end):
                        sortkey = (self.list[idx] & ~disc) ^ uint_63
                        val = (sortkey >> shift) & self.radix - 1
                        count[val] += 1
                    if count[-1] == end - start:
                        temp_bucket_indexes.append((start, end))
                        count = [0 for _ in count]
                        continue
                    if count[0] > 1:
                        temp_bucket_indexes.append((start, start + count[0]))
                    for i in range(1, self.radix):
                        if count[i] > 1:
                            temp_bucket_indexes.append(
                                (start + count[i - 1], start + count[i] + count[i - 1])
                            )
                        count[i] += count[i - 1]
                    for i in range(start, end):
                        sortkey = (self.list[i] & ~disc) ^ uint_63
                        val = (sortkey >> shift) & self.radix - 1
                        temp_list[count[val] - 1 + start] = self.list[i]
                        count[val] -= 1
                    count = [0 for _ in count]
                    disc = ((1 << shift - self.base) - 1) if k > 0 else 0
                bucket_indexes = temp_bucket_indexes
                self.setslice(temp_list)
                if not bucket_indexes:
                    return
    return Radixsort