from log_reader import read_log

def get_failed_reads(log, merge = False):
    err4xx = []
    err5xx = []
    for singleLog in log:
        if len(singleLog) < 10:
            continue

        if 400 <= singleLog[9] < 500:
            err4xx.append(singleLog)
        elif 500 <= singleLog[9] < 600:
            err5xx.append(singleLog)

    if merge:
        return err4xx + err5xx
    else:
        return err4xx, err5xx

if __name__ == "__main__":
    log = read_log()

 #   print(get_failed_reads(log))
  #  print(get_failed_reads(log, merge = True))
    print(get_failed_reads([]))
    print(get_failed_reads([], merge = True))