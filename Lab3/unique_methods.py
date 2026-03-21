from log_reader import read_log

def get_unique_methods(log):
    uniq_methods = set()
    for singleLog in log:
        if len(singleLog) > 6:
            method = singleLog[6]
            uniq_methods.add(method)

    return list(uniq_methods)
if __name__ == "__main__":
    log = read_log()

    print(get_unique_methods(log))
    print(get_unique_methods([]))