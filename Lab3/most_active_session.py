from log_reader import read_log
from log_dict import log_to_dict
def get_most_active_session(log_dictionary):
    if not log_dictionary:
        return None
    return max(log_dictionary, key= lambda uid: len(log_dictionary[uid]))

if __name__ == '__main__':
    log = read_log()
    log_dictionary = log_to_dict(log)
    print(get_most_active_session(log_dictionary))
    print(get_most_active_session({}))
