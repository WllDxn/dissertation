from math import ceil, pow, log
import sys
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
        return sys.maxint
    return -num if num < 0 else num

def print_arr(arr, min_bytes=63, base=1, usedisc = False):
    radix = int(pow(2,base))
    chars = max(len(str(n)) for n in arr)
    cols = ("\033[4m"
        " " * (chars)
        + ' | '        
    )
    print(cols, end="")
    for i in (f" {str(n)}" if n > 9 else f"  {str(n)}" for n in range(min_bytes,-1,-1)):
        print(i, end="")
    print('\033[0m')
    uint_63 = ~((1 << int_bytes(9223372036854775807, 2) - 1) - 1)
    ovf = True
    for i in arr:
        s = " "*(chars-len(str(i))) + str(i) + " | "
        shift = min_bytes * base
        disc = ((1 << shift + base) - 1) if (not ovf) else ((1 << (shift)) - 1)
        for j in range(min_bytes, -1, -1):
            sortkey = (i & ~disc) ^ uint_63 if usedisc else i ^ uint_63
            val = (sortkey >> base*j) & radix - 1
            s += (" "*(3-len(str(val)))) + str(val)
            disc = ((1 << (base*j - base)) - 1) if j > 0 else 0
        print(s)

print_arr([-123123,1345,2543,3153,-6134534])
        