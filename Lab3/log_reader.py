import sys
from datetime import datetime

class Log:
    def __init__(self, fields):
        self.ts = datetime.fromtimestamp(float(fields[0]))
        self.uid = fields[1]
        self.idOrigH = fields[2]
        self.idOrigP = int(fields[3])
        self.idRespH = fields[4]
        self.idRespP = int(fields[5])
        self.method = fields[7]
        self.host = fields[8]
        self.uri = fields[9]
        self.size = fields[13]
        self.statusCode = int(fields[14]) if fields[14] != "-" else 0



def read_log(file_path):
    separator = "\t"
    logList = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for log in file:
                log = log.strip()

                if not log:
                    continue

                fields = log.split(separator)
                if len(fields) < 15:
                    continue

                new_log = Log(fields)

                logList.append(new_log)

            if not logList:
                print("Nie znaleziono żadnych logów w podanym pliku")
    except FileNotFoundError:
        print("Nie znaleziono pliku")
    return logList

