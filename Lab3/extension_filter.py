from log_reader import read_log

def get_entries_by_extension(log, ext):
    def check(singleLog):
        uri = singleLog[8]
        firstSplit = uri.split("?")
        singleLogExt = firstSplit[0].split(".")[-1]
        return singleLogExt == ext

    return list(filter(check, log))

if __name__ == "__main__":
    log = read_log()

    print(get_entries_by_extension(log, "nsf"))
    print(get_entries_by_extension(log, "jpg"))
    print(get_entries_by_extension(log, "żurek"))