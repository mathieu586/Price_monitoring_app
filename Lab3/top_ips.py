from log_reader import read_log

def get_top_ips(log, n = 10):
    if type(n) is not int or n < 0:
        print("Niepoprawne n")
        return []

    ipPresance = {}

    for singleLog in log:
        if len(singleLog) < 3:
            continue

        hostIp = singleLog[2]
        if hostIp in ipPresance:
            ipPresance[hostIp] += 1
        else:
            ipPresance[hostIp] = 1

    sortedIps = sorted(ipPresance.items(), key=lambda x: x[1], reverse=True)

    return sortedIps[0:n]

if __name__ == "__main__":
    log = read_log()

    print(get_top_ips(log, 0))
    print(get_top_ips(log, -1))
    print(get_top_ips(log, "A"))
    print(get_top_ips(log))
    print(get_top_ips([]))