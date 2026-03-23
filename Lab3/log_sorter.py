import sys
from log_reader import read_log

def sort_log(log, index):
    if not log:
        print("Pusty log - brak danych do sortowania")
        return []

    if index >= len(log[0]) or index < 0:
        print("Podano niepoprawny indeks - zwrócono nieposortowane")
        return log

    def get_element(single_log):
        return single_log[index]

    try:
        return sorted(log, key = get_element)
    except(IndexError):
        print(f"Błąd: Niepoprawny index")
        return log

if __name__ == "__main__":
    log = read_log()

    print(sort_log(log, 0))
    print(sort_log(log, 30))
    print(sort_log([], 0))

