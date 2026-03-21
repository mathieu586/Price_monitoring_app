import sys
from log_reader import read_log

def sort_log(log, index):
    def get_element(single_log):
        return single_log[index]

    try:
        return sorted(log, key = get_element)
    except(IndexError):
        print(f"Błąd: Niepoprawny index")
        return log

if __name__ == "__main__":
    if(len(sys.argv)) < 2:
        print("Nie podano indeksu")
        sys.exit()

    log = read_log()
    try:
        index = int(sys.argv[1])
        sort_log(log, index)
    except(IndexError, ValueError):
        print("Podano nieprawidłowy argument")