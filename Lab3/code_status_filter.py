import sys
from log_reader import read_log

def get_entries_by_code(log, code):
    try:
        code = int(code)
    except(ValueError):
        print("Podano nieprawidłowy kod http")
        return []

    def check(singleLog):
        if(len(singleLog) < 10):
            print("Znaleziono błędny log")
            return False
        return singleLog[9] == code

    return list(filter(check, log))

if __name__ == "__main__":
    log = read_log()

    print(get_entries_by_code(log, 404))
    print(get_entries_by_code(log, 2424))
    print(get_entries_by_code(log, "aaa"))

