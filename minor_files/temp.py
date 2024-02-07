def insertion_sort(l):
    for step in range(len(l)):
        key = l[step]
        j = step - 1
        while j >= 0 and key < l[j]:
            l[j + 1] = l[j]
            j = j - 1
        l[j + 1] =  key
        print(l)
insertion_sort([1235,234,657,24,5637,4256,452])