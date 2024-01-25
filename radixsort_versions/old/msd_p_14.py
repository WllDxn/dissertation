from math import pow, floor, log



def absolute(num):
    """
    Custom implementation of abs(Num)
    :param num: Number to find absolute value of
    :return: absolute value of num
    """

    return -num if num < 0 else num


def int_bytes(i, radix):
    """
    Retrieves the minimum number of bytes required to identify an integer.

    :param radix: Number base
    :param i: Input integer
    :return: Number of bytes used to identify integer
    """
    return int(floor(log(absolute(i)) / log(radix)))+1


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
            self.base = 14
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
            min_bytes = int_bytes(self.list_abs_max(checkorder=True), self.radix)
            if self.ordered == True:
                return
            if self.reverseOrdered == True:
                self.reverseSlice()
                return
            bucket_indexes = [(0, self.listlength)]
            uint_63 = ((1) << ((min_bytes+1) * self.base) - 1)
            for k in xrange(min_bytes, -1, -1):
                shift = k * self.base
                temp_indexes = []
                for start, end in bucket_indexes:
                    if start + 1 == end:
                        continue
                    if (end - start) < 12000:
                        self.insertion_sort(start, end)
                        continue
                    buckets = [[] for _ in xrange(self.radix)]
                    for i in xrange(start, end):
                        sortkey = (self.list[i]) ^ uint_63
                        val = ((sortkey >> shift)) & self.radix - 1
                        buckets[val].append(self.list[i])
                    if len([len(b) for b in buckets if b != []]) == 1:
                        temp_indexes.append((start, end))
                        continue
                    accum = 0
                    for bucket in buckets:
                        if len(bucket) > 1:
                            temp_indexes.append(
                                (start + accum, start + accum + len(bucket))
                            )
                        for item in bucket:
                            self.setitem(start + accum, item)
                            accum += 1
                bucket_indexes = temp_indexes
                if len(bucket_indexes) == 0:return

    return Radixsort
