import sys
from datetime import datetime


def read_log():
    separator = "\t"
    logList = []

    for log in sys.stdin:
        log = log.strip()

        if not log:
            continue

        fields = log.split(separator)
        if len(fields) < 15:
            continue


        ts = datetime.fromtimestamp(float(fields[0]))
        uid = fields[1]
        idOrigH = fields[2]
        idOrigP = int(fields[3])
        idRespH = fields[4]
        idRespP = int(fields[5])
        method = fields[7]
        host = fields[8]
        uri = fields[9]
        statusCode = int(fields[14])  if fields[14] != "-" else 0

        logData = (ts, uid, idOrigH, idOrigP, idRespH, idRespP, method, host, uri, statusCode)
        logList.append(logData)

    if not logList:
        print("Nie znaleziono żadnych logów w podanym pliku")

    return logList

if __name__ == "__main__":
    read_log()