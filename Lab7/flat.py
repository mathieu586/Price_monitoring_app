def flatten(ls):
    if not ls:
        return []
    head, *tail = ls
    return (flatten(list(head)) if isinstance(head, (list,tuple)) else [head]) + flatten(tail)

if __name__ == '__main__':
    print(flatten([1, [2,3], [[4,5], 6]]))
    print(flatten([1,2,3,4, (1,2)]))
    print(flatten([[[[[[[1]]],2]]]]))
    print(flatten([[[[[[[]]]]]]]))
