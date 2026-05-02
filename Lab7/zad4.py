def make_generator(f):
    def generator():
        n = 1
        while True:
            yield f(n)
            n += 1


    return generator()


def fibonacci(n):
    val = 1
    prev = 0
    for _ in range(n):
        temp = val
        val = prev + val
        prev = temp

    return prev


if __name__ == "__main__":
    fib_generator = make_generator(fibonacci)

    for i in range(10):
        print(next(fib_generator))


    ar_generator = make_generator(lambda x: x + 1)
    geo_generator = make_generator(lambda x: 2 ** x)
    pot_generator = make_generator(lambda x: x ** 2)

    for i in range(10):
        print(f"-----------------\nIteracja {i}:")
        print(f"arytmetyczny: {next(ar_generator)}\ngeometryczny: {next(geo_generator)}\npotęgowy: {next(pot_generator)}")


