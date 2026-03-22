from log_reader import read_log
from log_dict import log_to_dict
from collections import Counter
from datetime import datetime
def print_dict_entry_dates(log_diction):
    for uid, entries in log_diction.items():
        if not entries:
            continue
        ip_set = set(e["idOrigH"] for e in entries)
        host_set = set(e["host"] for e in entries)
        num_requests = len(entries)
        timestamps = [e["ts"] for e in entries]

        if isinstance(timestamps[0], str):
            timestamps = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]
        first_ts = min(timestamps)
        last_ts = max(timestamps)

        method_counts = Counter(e["method"] for e in entries)
        method_percent = {m: round(c / num_requests * 100, 2) for m, c in method_counts.items()}

        success_2xx = sum(1 for e in entries if 200 <= e["statusCode"] < 300)
        success_ratio = round(success_2xx / num_requests * 100, 2)

        print(f"UID: {uid}")
        print(f"  IP: {', '.join(ip_set)}")
        print(f"  Host: {', '.join(host_set)}")
        print(f"  Liczba żądań: {num_requests}")
        print(f"  Pierwsze żądanie: {first_ts}")
        print(f"  Ostatnie żądanie: {last_ts}")
        print(f"  Udział metod HTTP (%): {method_percent}")
        print(f"  Stosunek 2xx do wszystkich (%): {success_ratio}% \n")

if __name__ == "__main__":
    logList = read_log()
    log_diction = log_to_dict(logList)
    print_dict_entry_dates(log_diction)
    print_dict_entry_dates({})
