from log_reader import read_log

def detect_sus(log, threshold = 100):
    try:
        threshold = int(threshold)
    except(ValueError):
        print("Podano nieprawidłowy threshold")
        return []

    ip_counts = {}
    ip_404 = {}
    ip_times = {}

    for entry in log:
        ip = entry[2]
        code = entry[9]
        ts = entry[0]

        if ip in ip_counts:
            ip_counts[ip] += 1
        else:
            ip_counts[ip] = 1

        if code == 404:
            if ip in ip_404:
                ip_404[ip] += 1
            else:
                ip_404[ip] = 1

        if ip not in ip_times:
            ip_times[ip] = []
        ip_times[ip].append(ts)

    sus = []
    for ip in ip_counts:
        total = ip_counts[ip]
        err_404 = ip_404.get(ip, 0)

        if total >= threshold:
            sus.append(ip)
            continue

        if total > 0 and err_404 / total > 0.5:
            sus.append(ip)
            continue

        times = sorted(ip_times[ip])
        fast_requests = 0

        for i in range(1, len(times)):
            diff = (times[i] - times[i - 1]).total_seconds()
            if diff < 0.1:
                fast_requests += 1

        if fast_requests > 10:
            sus.append(ip)
    return sus

if __name__ == '__main__':
    log = read_log()
    print(detect_sus(log))
    print(detect_sus(log, threshold=250))
    print(detect_sus(log, threshold="abcdefg"))