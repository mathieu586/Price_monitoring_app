

def liczba(liczby):
    return 0 if not liczby else (liczby[0] + liczba(liczby[1:]) if liczby[0] % 2 != 0 else liczba(liczby[1:]))

def median(liczby):
    n = len(liczby)
    return (liczby[n//2] if n % 2 != 0 else (liczby[n//2] + liczby[n//2 - 1]) / 2) if liczby else 0

def pierwiastek(x, eps, y=1):
    return (y if y >= 0 and abs(y*y - x) < eps else pierwiastek(x, eps, (y + (x/y))/2)) if x >= 0 else None

if __name__ == "__main__":
    print("=========== a =============")
    print(liczba([1, 0, 5]))
    print(liczba([1, 0, 5, 4, 1, 10]))
    print(liczba([]))
    print("=========== b =============")
    print(median([1,1,19,2,3,4,4,5,1]))
    print(median([1, 2, 3, 4]))
    print(median([]))
    print("=========== c =============")
    print(pierwiastek(3, 0.1))
    print(pierwiastek(1, 0.1))
    print(pierwiastek(-1, 0.1))

