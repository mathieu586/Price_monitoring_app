import sys

from log_reader import read_log

def get_extension_stats(log):
    stats = {}
    for entry in log:
        uri = entry[8]

        if "." in uri:
            extension = uri.split(".")[-1].lower()
        else:
            extension = "None"

        stats[extension] = stats.get(extension, 0) + 1

    return stats

if __name__ == "__main__":
    log = read_log()
    print(get_extension_stats(log))
    print(get_extension_stats([]))