from log_reader import read_log

def count_by_method(log):
    metCount = {}

    for singleLog in log:
        if len(singleLog) < 7:
            continue
        method = singleLog[6]

        if method in metCount:
            metCount[method] += 1
        else:
            metCount[method] = 1

    return metCount
if __name__ == "__main__":
    log = read_log()

    print(count_by_method(log))
    print(count_by_method([]))