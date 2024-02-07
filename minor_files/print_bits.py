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
        return sys.maxsize
    return -num if num < 0 else num

def print_arr(arr, base=12, tempdisc=0, usedisc=False, min_bytes=64,num=-1,vals=None):
    radix = int(pow(2,base))
    min_bytes=int_bytes(max([abs(x) for x in arr]),radix) if max(arr)!=0 else 0
    # if vals!=None:
    # if vals==None:
    #     min_bytes=64
    print('min: ', str(min_bytes), str((int_bytes((-sys.maxsize) - 1, radix))),str(vals))
    if min_bytes == int_bytes((-sys.maxsize) - 1, radix):
        uint_63 =  ~((1 << int_bytes(sys.maxsize, 2) - 1) - 1)
        # min_bytes -= 1
    else:
        uint_63 = ~((1 << int_bytes(sys.maxsize, 2)) - 1)
        min_bytes-=1
    out = [[] for _ in arr]
    curr = 0
    for idx, i in enumerate(arr):
        print(min_bytes)
        for j in range(min_bytes):
            sortkey = (i & ~tempdisc) ^ uint_63 if usedisc else i ^ uint_63
            val = (sortkey >> base*j) & radix - 1
            if num==j:
                curr=(sortkey >> 12*(j)) & 4095

            out[idx].append(val)
            if num==j and vals:
                out[idx].insert(0,curr)
        out[idx].reverse()
    # for i in range(len(arr)):
    #     out[i].insert(0, (arr[i]))
    
    return out
    
    

# def print_arr(arr, base=12, usedisc = False, num=-1, tempdisc=0):
#     # if num<8:return
#     radix = int(pow(2,base))
#     cdisc = 0
#     min_bytes = int_bytes(sys.maxsize, radix)
#     if min_bytes == int_bytes((-sys.maxsize) - 1, radix)-1:
#         uint_63 =  ~((1 << int_bytes(sys.maxsize, 2) - 1) - 1)
#         min_bytes -= 1
#         ovf = True
#     else:
#         uint_63 = ~((1 << int_bytes(sys.maxsize, 2)) - 1)
#         ovf = False
        
        
#     arr+=[(~tempdisc)^uint_63]
#     repeats = min_bytes+1 if base!=1 or ovf==True else min_bytes-1
#     chars = max(len(str(n)) for n in arr)
#     cols = ("\033[4m"
#         " " * (chars)
#         + ' | '        
#     )
#     intro =  (cols)
#     space = "" if radix<10 else "  "
#     space2 = "" if base<10 else " "
#     for i in (f"{space} {str(n)}" if n > 9 else f"{space}{space2}  {str(n)}" for n in range(repeats,-1,-1)):
#         intro += (i)
#     print(intro + '\033[0m')
    
    
    
    
    
#     # arr.append(uint_63)
#     for idx, i in enumerate(arr):

#         s = " "*(chars-len(str(i))) + str(i) + " | "
#         shift = min_bytes * base

#         disc = ((1 << shift+ base) - 1) if (not ovf) else ((1 << (shift)) - 1)
#         for j in range(repeats, -1, -1):




#         if min_bytes==62 and i!=(~tempdisc)^uint_63:
#             s += "  " + str((((i) ^ uint_63) >>base*num) & radix)
#         print(s)
#     print(min_bytes)
#     if num!=-1:
#         snum = 5 if space== "" else 6
#         print(" "*(chars+snum) +(" "*((3+len(space))*(min_bytes-num)))  +'^'+str(tempdisc))
if __name__=='__main__':
    print_arr([5433])
        