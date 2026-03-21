from log_reader import read_log

def get_entries_by_addr(log, addr):
    separated = addr.split(".")

    if len(separated) == 4:
        try:
            for number in separated:
                num = int(number)
                if num < 0 or num > 255:
                    print("Podano nieprawidłowy adres hosta")
                    return []
        except(ValueError):
            print("Podano adres hosta nieprawidłowego typu")


    def check(singleLog):
        if(len(singleLog) != 10):
            print("Znaleziono błędny log")
            return False
        return singleLog[2] == addr or singleLog[7] == addr

    return list(filter(check, log))

if __name__ == "__main__":
    log = read_log()

    get_entries_by_addr(log, "192.168.202.79")
    get_entries_by_addr(log, "300.168.202.79")
    get_entries_by_addr(log, "żurek")



