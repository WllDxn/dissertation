from math import ceil, log, pow
import sys
import gen_data
import os
import time
# bigbase = 6
# def int_bytes(i, radix):
#     """
#     Retrieves the minimum number of bytes required to identify an integer.

#     :param radix: Number base
#     :param i: Input integer
#     :return: Number of bytes used to identify integer
#     """

#     val =  int(ceil(round(log(absolute(i)) / log(radix), 6)))+1
#     return  val + 1 if val%radix==0 else val


# def absolute(num):
#     """
#     Custom implementation of abs(Num)
#     :param num: Number to find absolute value of
#     :return: absolute value of num
#     """
#     if num == (-sys.maxsize) - 1:
#         return sys.maxsize
#     return -num if num < 0 else num


# def make_radixsort_class(
#     setitem=None,
#     setslice=None,
# ):
#     if setitem is None:

#         def setitem(list, item, value):
#             list[item] = value

#     if setslice is None:

#         def setslice(list, slice, index):
#             list[index : index + len(slice)] = slice

#     class Radixsort(object):
#         def __init__(self, list, listlength=None):
#             self.list = list
#             self.base = bigbase
#             self.listlength = len(self.list)
#             self.radix = int(pow(2, self.base))

#         def setitem(self, item, value):
#             setitem(self.list, item, value)

#         def setslice(self, slice, index):
#             setslice(self.list, slice, index)

#         def list_abs_max(self, checkorder=False):
#             """
#             Returns the list item that will require the most bits to express. (the smallest or the largest value)
#             Also optinoally returns booleans stating whether the list is ordered or reverse ordered
#             :param checkorder: Flag that determines whether to check whether the list is ordered
#             :return: the maximum absolute value in the list
#             """

#             assert len(self.list) != 0
#             m = self.list[0]
#             n = self.list[0]
#             prev = self.list[0]
#             (ordered, reverseordered) = (True, True)
#             for i in range(1, len(self.list)):
#                 if self.list[i] > m:
#                     m = self.list[i]
#                 if self.list[i] < n:
#                     n = self.list[i]
#                 if checkorder:
#                     ordered &= self.list[i] >= prev
#                     reverseordered &= self.list[i] <= prev
#                     prev = self.list[i]
#             if checkorder:
#                 self.ordered = ordered
#                 self.reverseOrdered = reverseordered
#             return m if absolute(m) > absolute(n) else n

#         def insertion_sort(self, start, end):
#             for step in range(start, end):
#                 key = self.list[step]
#                 j = step - 1
#                 while j >= 0 and key < self.list[j]:
#                     self.setitem(j + 1, self.list[j])
#                     j = j - 1
#                 self.setitem(j + 1, key)

#         def reverseSlice(self, start=0, stop=0):
#             if stop == 0:
#                 stop = self.listlength - 1
#             while start < stop:
#                 i = self.list[start]
#                 j = self.list[stop]
#                 self.setitem(start, j)
#                 self.setitem(stop, i)
#                 start += 1
#                 stop -= 1

#         def sort(self):
#             if self.listlength < 2:
#                 return
#             listmax = self.list_abs_max(checkorder=True)
#             min_bytes = int_bytes(listmax, self.radix)
#             if self.ordered == True:
#                 return
#             if self.reverseOrdered == True:
#                 self.reverseSlice()
#                 return
#             if min_bytes == int_bytes((-sys.maxsize) - 1, self.radix):
#                 uint_63  = ~((1 << int_bytes(listmax, 2) - 1) - 1)
#             else:
#                 uint_63 = ~((1 << int_bytes(listmax, 2)) - 1)
#             bucket = [[] for _ in range(self.radix)]
#             for i in range(min_bytes):
#                 shift = (self.base) * i
#                 for num in self.list:
#                     sortkey = num  ^ uint_63
#                     val = (sortkey >> shift) & self.radix - 1
#                     bucket[val].append(num)
#                 if len([b for b in bucket if b != []]) == 1:
#                     continue
#                 index = 0
#                 for bdx, b in enumerate(bucket):
#                     self.setslice(b, index)
#                     index += len(b)
#                     bucket[bdx] = []

#     return Radixsort
# r = make_radixsort_class()
def test_1():
    for i in range(1,64):
        print(f'size: {i}  \t',end='')
        for b in [6]:#,8,10,12,14,16]:
            bigbase = b 
            data = gen_data.gen_list(1000000, int(pow(2,i))-1)
            data.sort()
            p = f'\033[32m{b}' if sorted(data) == data else f'\033[31m{b}'
            print(f'{p}', end=' ')
        print('\033[0m')

if __name__=='__main__':
    d = '/home/will/dissertation/minor_files/arrslong'
for y in os.listdir(d):
    with open(d+'/'+y, 'r') as f:
        data = f.read().split(',')
        data = ([int(x) for x in data if x != ''])
        t = time.time()
        data.sort()
        p = f'\033[32m{time.time()-t}' if sorted(data) == data else f'\033[31m{time.time()-t}'
        print(f'{p}', end=' ')
        print('')