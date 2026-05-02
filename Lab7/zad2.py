def forall(pred, iterable):
    return not iterable or pred(iterable[0]) and forall(pred, iterable[1:])


def exists(pred, iterable):
    return bool(iterable) and (pred(iterable[0]) or exists(pred, iterable[1:]))


def atleast(n, pred, iterable):
    return n <= 0 or (bool(iterable) and (atleast(n - 1, pred, iterable[1:]) if pred(iterable[0]) else atleast(n, pred, iterable[1:])))


def atmost(n, pred, iterable):
    return n >= 0 and (not iterable or (atmost(n - 1, pred, iterable[1:]) if pred(iterable[0]) else atmost(n, pred, iterable[1:])))
