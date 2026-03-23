from log_reader import read_log
from top_uris import get_top_uris
from top_ips import get_top_ips
from status_counter import count_status_classes
from count_method import count_by_method
def analyze_log(log):
    if not log:
        return {}

    result = {}

    top_ips = get_top_ips(log, 1)
    result["top_ip"] = top_ips[0] if top_ips else None

    top_uris = get_top_uris(log, 1)
    result["top_uri"] = top_uris[0] if top_uris else None

    status_classes = count_status_classes(log)
    result["status_classes"] = status_classes

    result["methods"] = count_by_method(log)

    errors = status_classes.get("4xx", 0) + status_classes.get("5xx", 0)
    result["errors"] = errors

    result["total_requests"] = len(log)

    return result

if __name__ == "__main__":
    log = read_log()
    print(analyze_log(log))
    print(analyze_log([]))