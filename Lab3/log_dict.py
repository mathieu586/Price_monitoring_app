from log_reader import read_log
from entry_dict import entry_to_dict
def log_to_dict(log):
    grouped = {}
    for entry in log:
        entry_dict = entry_to_dict(entry)
        uid = entry_dict['uid']
        if uid not in grouped:
            grouped[uid] = []
        grouped[uid].append(entry_dict)
    return grouped

if __name__ == '__main__':
    log = read_log()
    print(log_to_dict(log[:5]))
    print(log_to_dict([]))
