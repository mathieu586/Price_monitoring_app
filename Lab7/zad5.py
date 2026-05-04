from functools import lru_cache
from zad4 import make_generator, fibonacci
def make_generator_mem(f):
    memoized = lru_cache(maxsize=None)(f)
    return make_generator(memoized)
counter_mem = 0
def take(n, gen):
    return [next(gen) for _ in range(n)]

@lru_cache(maxsize=None)
def fib_mem(n):
    global counter_mem
    counter_mem += 1
    if n<=1:
        return n
    return fib_mem(n-1)+fib_mem(n-2)

if __name__ == '__main__':
    gen1 = make_generator(fib_mem)
    print(take(30, gen1))
    print(counter_mem)
    geo_generator = make_generator_mem(lambda x: 2 ** x)
    print(take(10, geo_generator))
    pot_generator = make_generator_mem(lambda x: x ** 2)
    print(take(10, pot_generator))