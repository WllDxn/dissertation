from math import pow, ceil, log
from rpython.rlib.rarithmetic import r_uint


def absolute(num):
    """
    Custom implementation of abs(Num)
    :param num: Number to find absolute value of
    :return: absolute value of num
    """

    return -num if num < 0 else num


def list_abs_max(arr):
    """
    Returns the list item that will require the most bits to express. (the smallest or the largest value)

    :param arr: Input list of integers
    :return: the maximum absolute value in the list
    """

    assert len(arr) != 0
    m = arr[0]
    n = arr[0]
    for i in xrange(1, len(arr)):
        if arr[i] > m:
            m = arr[i]
        if arr[i] < n:
            n = arr[i]
    return m if absolute(m) > absolute(n) else n


def int_bytes(i, radix):
    """
    Retrieves the minimum number of bytes required to identify an integer.

    :param radix: Number base
    :param i: Input integer
    :return: Number of bytes used to identify integer
    """
    return int(ceil(log(absolute(i)) / log(radix)))


def make_radixsort_class(
    getitem=None,
    setitem=None,
    length=None,
):
    if getitem is None:

        def getitem(list, item):
            return list[item]

    if setitem is None:

        def setitem(list, item, value):
            list[item] = value

    if length is None:

        def length(list):
            return len(list)

    class Radixsort(object):
        def __init__(self, list, listlength=None):
            self.list = list
            self.base = 8
            if listlength is None:
                listlength = length(list)
            self.listlength = listlength
            self.radix = int(pow(2, self.base))

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
            min_bytes = int_bytes(list_abs_max(self.list), int(pow(2, self.base)))
            max_bytes = int_bytes(9223372036854775807, self.radix)
            uint_63 = (r_uint(1) << 63)
            counts = [[0 for _ in xrange(self.radix)] for _ in xrange(min_bytes + 1)]
            (ordered, reverseordered) = (True, True)
            prev = self.list[0]
            for num in self.list:
                for i in xrange(min_bytes + 1):
                    if i != min_bytes:
                        shift = (self.base) * i
                    else:
                        shift = self.base * (max_bytes - 1)
                    sortkey = (r_uint(num)) ^ uint_63
                    val = (sortkey >> shift) & self.radix - 1
                    counts[i][val] += 1
                ordered &= num >= prev
                reverseordered &= num <= prev
                prev = num
            if ordered:
                return
            if reverseordered:
                self.reverseSlice()
                return
            skip = []
            for i in xrange(min_bytes + 1):
                for j in xrange(1, self.radix):
                    if counts[i][j] == self.listlength:
                        skip.append(i)
                    counts[i][j] += counts[i][j - 1]
            for i in xrange(min_bytes + 1):
                if i in skip:
                    continue
                shift = (
                    (self.base) * i if i != min_bytes else self.base * (max_bytes - 1)
                )
                temp_list = [0 for _ in xrange(self.listlength)]
                indexes = []
                (ordered, reverseordered) = (True, True)
                prev = self.list[0]
                for j in xrange(self.listlength - 1, -1, -1):
                    num = self.list[j]
                    sortkey = (r_uint(num)) ^ uint_63
                    val = (sortkey >> shift) & self.radix - 1
                    temp_list[counts[i][val] - 1] = self.list[j]
                    indexes.append(counts[i][val] - 1)
                    counts[i][val] -= 1
                    ordered &= num >= prev
                    reverseordered &= num <= prev
                    prev = num
                if ordered:
                    return
                if reverseordered:
                    self.reverseSlice()
                    return
                for j in indexes:
                    self.setitem(j, temp_list[j])

 
    return Radixsort
