from log_reader import read_log
def get_top_uris(log, n = 10):
    if type(n) is not int or n < 0:
        print("Niepoprawne n")
        return []

    urisPresent = {}

    for singleLog in log:
        uri = singleLog[8]
        if uri in urisPresent:
            urisPresent[uri] += 1
        else:
            urisPresent[uri] = 1

    sorted_uris = sorted(urisPresent.items(), key=lambda x: x[1], reverse=True)
    return sorted_uris[:n]

if __name__ == "__main__":
    log = read_log()
    print(get_top_uris(log, 0))
    print(get_top_uris(log, 1))
    print(get_top_uris(log, "A"))
    print(get_top_uris(log))
    print(get_top_uris([]))
    print()
