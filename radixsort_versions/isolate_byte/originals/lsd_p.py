from math import ceil, log, pow
import sys


def int_bytes(i, radix):
    """
    Retrieves the minimum number of bytes required to identify an integer.

    :param radix: Number base
    :param i: Input integer
    :return: Number of bytes used to identify integer
    """

    return int(ceil(log(abs(i)) / log(radix))) + 1


def list_abs_max(arr):
    """
    Returns the list item that will require the most bits to express. (the smallest or the largest value)

    :param arr: Input list of integers
    :return: the maximum absolute value in the list
    """

    assert len(arr) != 0
    m = arr[0]
    n = arr[0]
    for i in range(1, len(arr)):
        if arr[i] > m:
            m = arr[i]
        if arr[i] < n:
            n = arr[i]
    return m if abs(m) > abs(n) else n


def absolute(num):
    """
    Custom implementation of abs(Num)
    :param num: Number to find absolute value of
    :return: absolute value of num
    """
    if num == (-sys.maxint) - 1:
        return sys.maxint
    return -num if num < 0 else num


def make_radixsort_class(
    setitem=None,
    length=None,
):
    if setitem is None:

        def setitem(list, item, value):
            list[item] = value

    if length is None:

        def length(list):
            return len(list)

    class Radixsort(object):
        def __init__(self, list, listlength=None):
            self.list = list
            self.base = 6
            if listlength is None:
                listlength = length(list)
            self.listlength = listlength
            self.radix = int(pow(2, self.base))
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

        def insertion_sort(self, start, end):
            for step in xrange(start, end):
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
            if min_bytes == int_bytes((-sys.maxint) - 1, self.radix):
                uint_63 = uint_63 = ~((1 << int_bytes(listmax, 2) - 1) - 1)
                min_bytes -= 1
                ovf = True
            else:
                uint_63 = ~((1 << int_bytes(listmax, 2)) - 1)
                ovf = False
            disc = 0
            for i in xrange(min_bytes + 1):
                bucket = [[] for _ in xrange(self.radix)]
                shift = (self.base) * i
                for num in self.list:
                    sortkey = (num & ~disc) ^ uint_63
                    val = (sortkey >> shift) & self.radix - 1
                    bucket[val].append(num)
                if len([b for b in bucket if b != []]) == 1:
                    continue
                for jdx, j in enumerate([num for sublist in bucket for num in sublist]):
                    self.setitem(jdx, j)
                disc = (
                        ((1 << shift) - 1)
                        if (not ovf) or i < min_bytes 
                        else ((1 << (shift - self.base)) - 1)
                    )

    return Radixsort
