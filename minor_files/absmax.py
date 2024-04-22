import sys
def list_abs_max(lis):
    assert len(lis) != 0
    m = lis[0]
    n = lis[0]
    prev = lis[0]
    (ordered, reverse_ordered) = (True, True)
    for i in range(1, len(lis)):
        if lis[i] > m:
            m = lis[i]
        if lis[i] < n:
            n = lis[i]
        ordered &= lis[i] >= prev
        reverse_ordered &= lis[i] <= prev
        prev = lis[i]
    return m if absolute(m) > absolute(n) else n
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
    if num == (-sys.maxsize) - 1:
        return sys.maxsize
    return -num if num < 0 else num

for i in range(-1, 2):
    print(pow(2,12)+i ,int_digits(pow(2,12)+i, 6), -(pow(2,12)+i) ,int_digits(-(pow(2,12)+i), 6))
    print(list_abs_max([pow(2, 12)+i, -(pow(2, 12)+i)]))