
import sys
from math import pow
def is_sorted(lst, key=lambda x: x, p=True):
    s = True
    out = ""
    for i, el in enumerate(lst[1:]):
        if key(el) < key(lst[i]):
            out += '\033[0;31m'+str(el) + ", "
            s = False
        else:
            out += '\033[0;32m'+str(el) + ", "            
    if not s: print(out)
    return s

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
            list[index : index + len(slice)] = slice

    class Radixsort(object):
        def __init__(self, list, list_length=None):
            self.list = list
            self.base = 2
            self.list_length = len(self.list)
            self.radix = int(pow(2, self.base))

        def list_abs_max(self):
            assert len(self.list) != 0
            m = self.list[0]
            n = self.list[0]
            prev = self.list[0]
            (self.ordered, self.reverse_ordered) = (True, True)
            for i in range(1, len(self.list)):
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
            assert index >= 0
            setslice(self.list, slice, index)

        def insertion_sort(self, start, end):
            for step in range(start, end):
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

            nextcount = [0 for _ in xrange(self.radix)]
            count = [0 for _ in xrange(self.radix)]
            for j in xrange(self.list_length):
                masked_input = self.list[j] ^ bit_mask
                curr_digit = (masked_input) & (self.radix - 1)
                count[curr_digit] += 1

            temp_list = self.list[:]
            skip = []
            for i in xrange(list_max_digits):
                if i not in skip:
                    for j in xrange(1, self.radix):                    
                        count[j] += count[j - 1]
                        nextcount[j] = 0
                    nextcount[0] = 0
                shift = (self.base) * i
                for j in xrange(self.list_length - 1, -1, -1):
                    masked_input = (self.list[j]) ^ bit_mask
                    if i not in skip:
                        curr_digit = ((masked_input >> shift)) & (self.radix - 1)
                        temp_list[count[curr_digit] - 1] = self.list[j]
                        count[curr_digit] -= 1
                    if i < list_max_digits-1:
                        next_curr_digit = (masked_input >> (self.base + shift)) & (self.radix - 1)
                        nextcount[next_curr_digit] += 1
                        if nextcount[next_curr_digit] == self.list_length:
                            skip.append(i+1)
                if i not in skip:
                    self.setslice(temp_list)
                    count = nextcount[:]

    return Radixsort