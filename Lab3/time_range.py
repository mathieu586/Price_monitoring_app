import datetime

def get_entries_in_time_range(log, start=None, end=None):
    if (start is not None and not isinstance(start, datetime.datetime)) or (end is not None and not isinstance(end, datetime.datetime)):
        print("Argument start i end musi być datą")
        return []

    if not log:
        return []

    min_date = min(log, key=lambda x: x.ts)
    max_date = max(log, key=lambda x: x.ts)

    if not start:
        start = min_date.ts

    if not end:
        end = max_date.ts

    output = []
    for singleLog in log:
        ts = singleLog.ts

        if start <= ts <= end:
            output.append(singleLog)

    return output

