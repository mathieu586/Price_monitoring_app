from log_reader import read_log
def count_status_classes(log):
    result = {}

    for singleLog in log:
        code = singleLog[9]
        try:
            code = int(code)
        except(ValueError, TypeError):
            continue

        if code == 0:
            continue

        class_code = f"{code // 100}xx"
        if class_code in result:
            result[class_code] += 1
        else:
            result[class_code] = 1
    return result
if __name__ == "__main__":
    log = read_log()
    print(count_status_classes(log))
    print(count_status_classes([]))
