from log_reader import read_log
import datetime

def get_entries_in_time_range(log, start, end):
    if not isinstance(start, datetime.datetime) or  not isinstance(end, datetime.datetime):
        print("Argument start i end musi być datą")
        return []

    output = []
    for singleLog in log:
        if len(singleLog) < 1:
            continue
        ts = singleLog[0]

        if start <= ts < end:
            output.append(singleLog)

    return output

if __name__ == "__main__":
    log = read_log()

    print(get_entries_in_time_range(log, datetime.datetime(2012, 3, 15, 13, 30, 2), datetime.datetime(2012, 3, 16, 13, 30, 6)))
    print(get_entries_in_time_range([], datetime.datetime(2012, 3, 16, 13, 30, 2), datetime.datetime(2012, 3, 16, 13, 30, 6)))
    print(get_entries_in_time_range(log, datetime.datetime(2020, 3, 16, 13, 30, 2), datetime.datetime(2012, 3, 16, 13, 30, 6)))
    print(get_entries_in_time_range(log, 12, 23))
