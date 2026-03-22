from log_reader import read_log
def entry_to_dict(entry):
    if not isinstance(entry, (tuple, list)) or len(entry) != 10:
        raise ValueError("Nieprawidłowe entry")
    return {
        "ts": entry[0],
        "uid": entry[1],
        "idOrigH": entry[2],
        "idOrigP": entry[3],
        "idRespH": entry[4],
        "idRespP": entry[5],
        "method": entry[6],
        "host": entry[7],
        "uri": entry[8],
        "statusCode": entry[9]
    }

if __name__ == "__main__":
    log = read_log()
    try:
        print(entry_to_dict(log[0]))
        print(entry_to_dict(log[922]))
        print(entry_to_dict([]))
    except ValueError as e:
        print("Błąd: ", e)