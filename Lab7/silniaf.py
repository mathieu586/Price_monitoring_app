def silnia(n):
    return n*silnia(n-1) if n > 1 else 1 if n >=0 else 0

def parzyste(lista):
    return (1 + parzyste(lista[1:]) if lista[0] % 2 == 0 else parzyste(lista[1:])) if bool(lista) else 0

if __name__ == "__main__":
    print(silnia(5))
    print(silnia(-10))

    print(parzyste([1, 4, 6, 2, 0]))
    print(parzyste([3, 1, 5]))