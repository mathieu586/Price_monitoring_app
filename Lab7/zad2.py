def forall(pred, iterable):
    return not iterable or pred(iterable[0]) and forall(pred, iterable[1:])


def exists(pred, iterable):
    return bool(iterable) and (pred(iterable[0]) or exists(pred, iterable[1:]))


def atleast(n, pred, iterable):
    return n <= 0 or (bool(iterable) and (atleast(n - 1, pred, iterable[1:]) if pred(iterable[0]) else atleast(n, pred, iterable[1:])))


def atmost(n, pred, iterable):
    return n >= 0 and (not iterable or (atmost(n - 1, pred, iterable[1:]) if pred(iterable[0]) else atmost(n, pred, iterable[1:])))


if __name__ == "__main__":
    pred = lambda x: x % 2 == 0
    nums = [0, 2, 3, 4, 5, 12, 23]
    nums2 = [0, 2, 4]
    napis = "test"
    empty = []

    print(forall(pred, nums))
    print(forall(pred, empty))
    print(forall(pred, nums2))
    print(forall(lambda x: x == "t", napis))
    print(forall(pred, [-4, -2, 0]))
    print()

    print(exists(pred, nums))
    print(exists(pred, empty))
    print(exists(lambda x: x == "t", napis))
    print(exists(pred, [-4, -2, 0]))
    print()

    print(atleast(5, pred, nums))
    print(atleast(3, pred, nums))
    print(atleast(0, pred, empty))
    print(atleast(2, lambda x: x == "t", napis))
    print(atleast(3, pred, [-4, -2, 0]))
    print()

    print(atmost(6, pred, nums))
    print(atmost(2, pred, nums))
    print(atmost(3, pred, empty))
    print(atmost(10, lambda x: x == "t", napis))
    print(atmost(10, pred, [-4, -2, 0]))




