from log_reader import read_log
from log_dict import log_to_dict

def get_session_paths(log):
    log_dictionary = log_to_dict(log)
    result = {}

    for uid,entries in log_dictionary.items():
        sorted_entries = sorted(entries, key=lambda item: item["ts"])
        result[uid] = [e["uri"] for e in sorted_entries]

    return result

if __name__ == "__main__":
    log = read_log()
    print(get_session_paths(log))
    print(get_session_paths([]))