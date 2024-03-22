import sys
from math import pow


def int_digits(i, base):
    l = 1
    v = 0 if i >= 0 else -1
    prev = i >> (l * base)
    while prev != v:
        l += 1
        new = i >> (l * base)
        if absolute(new) < absolute(prev):
            prev = i >> (l * base)
        else:
            return l
    return l


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
    setslice=None,
):
    if setitem is None:

        def setitem(list, item, value):
            list[item] = value

    if setslice is None:

        def setslice(list, slice, index):
            assert index >= 0
            list[index : index + len(slice)] = slice

    class Radixsort(object):
        def __init__(self, list, list_length=None):
            self.list = list
            self.base = 6
            self.list_length = len(self.list)
            self.radix = int(pow(2, self.base))

        def list_abs_max(self):
            assert len(self.list) != 0
            m = self.list[0]
            n = self.list[0]
            prev = self.list[0]
            (self.ordered, self.reverse_ordered) = (True, True)
            for i in xrange(1, len(self.list)):
                if self.list[i] > m:
                    m = self.list[i]
                if self.list[i] < n:
                    n = self.list[i]
                self.ordered &= self.list[i] >= prev
                self.reverse_ordered &= self.list[i] <= prev
                prev = self.list[i]
            return m if absolute(m) > absolute(n) else n

        def setitem(self, item, value):
            setitem(self.list, item, value)

        def setslice(self, slice, index=0):
            setslice(self.list, slice, index)

        def insertion_sort(self, start, end):
            for step in xrange(start, end):
                key = self.list[step]
                j = step - 1
                while j >= 0 and key < self.list[j]:
                    self.setitem(j + 1, self.list[j])
                    j = j - 1
                self.setitem(j + 1, key)

        def reverse_slice(self, start=0, stop=0):
            if stop == 0:
                stop = self.list_length - 1
            while start < stop:
                i = self.list[start]
                j = self.list[stop]
                self.setitem(start, j)
                self.setitem(stop, i)
                start += 1
                stop -= 1

        def slice_sorted(self, start=0, end=-1):
            end = end if end > -1 else self.list_length
            assert start >= 0
            assert end >= 0
            sublist_sorted, sublist_reverse_sorted = True, True
            for i, el in enumerate(self.list[start + 1 : end]):
                if el < self.list[start + i]:
                    sublist_sorted = False
                    if sublist_reverse_sorted == False:
                        return sublist_sorted, sublist_reverse_sorted
                if el > self.list[start + i]:
                    sublist_reverse_sorted = False
                    if sublist_sorted == False:
                        return sublist_sorted, sublist_reverse_sorted
            return sublist_sorted, sublist_reverse_sorted

        def sort(self):
            if self.list_length < 2:
                return
            list_max = self.list_abs_max()
            list_max_digits = int_digits(list_max, self.base)
            if self.ordered:
                return
            if self.reverse_ordered:
                self.reverse_slice()
                return
            max_bits = int(int_digits(list_max, 1))
            bit_mask = ~((1 << max_bits) - 1)
            if max_bits % self.base == 0 and max_bits != int_digits(
                (-sys.maxint) - 1, 1
            ):
                list_max_digits += 1
            count = [0 for _ in xrange(self.radix)]
            sublist_indexes = [(0, self.list_length)]
            for k in xrange(list_max_digits - 1, -1, -1):
                shift = k * self.base
                temp_sublist_indexes = []
                for start, end in sublist_indexes:
                    if start + 1 == end:
                        continue
                    sublist_sorted, sublist_reverse_sorted = self.slice_sorted(
                        start, end
                    )
                    if sublist_sorted:
                        continue
                    if sublist_reverse_sorted:
                        self.reverse_slice(start, end - 1)
                        continue
                    if (end - start) < 14:
                        self.insertion_sort(start, end)
                        continue
                    for idx in xrange(start, end):
                        masked_input = (self.list[idx]) ^ bit_mask
                        curr_digit = ((masked_input >> shift)) & self.radix - 1
                        count[curr_digit] += 1
                    if count[-1] == end - start:
                        temp_sublist_indexes.append((start, end))
                        count = [0 for _ in count]
                        continue
                    if count[0] > 1:
                        temp_sublist_indexes.append((start, start + count[0]))
                    for i in xrange(1, self.radix):
                        if count[i] > 1:
                            temp_sublist_indexes.append(
                                (start + count[i - 1], start + count[i] + count[i - 1])
                            )
                        count[i] += count[i - 1]
                    temp_list = [0 for _ in range(start, end)]
                    for i in xrange(start, end):
                        masked_input = (self.list[i]) ^ bit_mask
                        curr_digit = ((masked_input >> shift)) & self.radix - 1
                        temp_list[count[curr_digit] - 1] = self.list[i]
                        count[curr_digit] -= 1
                    count = [0 for _ in count]
                    self.setslice(temp_list, start)
                sublist_indexes = list(temp_sublist_indexes)
                if not sublist_indexes:
                    return

    return Radixsort
