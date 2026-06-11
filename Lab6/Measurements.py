import csv
import os
from datetime import datetime
from validator import OutlierDetector,ZeroSpikeDetector,ThresholdDetector
from time_series import TimeSeries


class Measurements:
    def __init__(self, path):
        self.path = path
        self.catalog = {}
        self.loadedseries = {}
        self.scan_dir()


    def scan_dir(self):
        if not os.path.isdir(self.path):
            raise NotADirectoryError("Ścieżka nie prowadzi do katalogu")
        for file in os.listdir(self.path):
            if not file.endswith(".csv"):
                continue
            filepath = os.path.join(self.path, file)
            nameparts = file[:-4].split("_")
            if len(nameparts) < 3:
                continue
            rokstr = nameparts[0]
            czas = nameparts[-1]
            wskaznik = "_".join(nameparts[1:-1])
            try:
                rok = int(rokstr)
            except ValueError:
                continue

            try:
                with open(filepath, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = [next(reader) for _ in range(6)]
            except (StopIteration, OSError):
                continue
            codes = rows[1][1:]
            for code in codes:
                key = (wskaznik,czas, rok, code.strip())
                self.catalog[key] = {
                    "filepath": filepath,
                    "wskaznik": wskaznik,
                    "czas": czas,
                    "rok": rok,
                    "kod": code.strip(),
                    "jednostka": "",
                }

    def loadfile(self, filepath, wskaznik, czas, rok):
        stationseries = {}
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header_rows = [next(reader) for _ in range(6)]
            stationcodes = [h.strip() for h in header_rows[1][1:]]
            jednostki = {
                code: header_rows[4][i + 1].strip()
                for i, code in enumerate(stationcodes)
                if i + 1 < len(header_rows[4])
            }
            for code in stationcodes:
                stationseries[code] = ([], [])

            for row in reader:
                if not row:
                    continue
                datestr = row[0].strip()
                date = None
                for fmt in ("%m/%d/%Y %H:%M", "%m/%d/%y %H:%M"):
                    try:
                        date = datetime.strptime(datestr, fmt)
                        break
                    except ValueError:
                        continue
                if date is None:
                    continue

                for i, code in enumerate(stationcodes):
                    col = i + 1
                    raw = row[col].strip() if col < len(row) else ""
                    if raw == "" or raw.lower() in ("nan", "none", "null", "-"):
                        val = None
                    else:
                        try:
                            val = float(raw)
                        except ValueError:
                            val = None
                    stationseries[code][0].append(date)
                    stationseries[code][1].append(val)

        for code, (daty, values) in stationseries.items():
            key = (wskaznik, czas, rok, code)
            jednostka = jednostki.get(code, self.catalog.get(key, {}).get("jednostka", ""))
            ts = TimeSeries(wskaznik, code, czas, daty, values, jednostka)
            self.loadedseries[key] = ts

    def ensureloaded(self, key):
        if key in self.loadedseries:
            return
        m = self.catalog.get(key)
        if m is None:
            raise KeyError(f"Brak serii dla klucza: {key}")
        self.loadfile(m["filepath"], m["wskaznik"], m["czas"], m["rok"])

    def getts(self, key):
        self.ensureloaded(key)
        return self.loadedseries[key]


    def __len__(self):
        return len(self.catalog)

    def __contains__(self, parameter_name):
        return any(key[0] == parameter_name for key in self.catalog)

    def get_by_parameter(self, param_name):
        res = []
        for key in self.catalog:
            if key[0] == param_name:
                res.append(self.getts(key))
        return res

    def get_by_station(self, station_code):
        res = []
        for key in self.catalog:
            if key[3] == station_code:
                res.append(self.getts(key))
        return res

    def detect_all_anomalies(self, validators, preload):
        if preload:
            for key in self.catalog:
                self.ensureloaded(key)
        results = {}
        for key, ts in self.loadedseries.items():
            results[key] = {}
            for validator in validators:
                name = type(validator).__name__
                results[key][name] = validator.analyze(ts)

        return results


    def __repr__(self):
        return f" Measurement: {self.path!r}, series: {self.catalog}, loaded: {self.loadedseries}"

    def __str__(self):
        return f" Measurement: {self.path!r}, series: {self.catalog}, loaded: {self.loadedseries}"

if __name__ == "__main__":
    m = Measurements(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\measurements")
    print(len(m))
    print("PM25" in m)
    print("nieistniejacy" in m)
    p = m.get_by_parameter("NO")
    if not p:
        print("Brak serii dla klucza")
    for x in p:
        print(x)
    p2 = m.get_by_parameter("niestniejacy")
    if not p2:
        print("Brak serii dla klucza")
    for x in p2:
        print(x)

    print("Get by station: \n")
    s = m.get_by_station("DsOsieczow21")
    if not s:
        print("Brak serii dla klucza")
    for x in s:
        print(x)
    s2 = m.get_by_station("niestniejacy")
    if not s2:
        print("Brak serii dla klucza")
    for x in s2:
        print(x)

    validators = [OutlierDetector(k=2.5), ZeroSpikeDetector(), ThresholdDetector(threshold=12)]
    anomalies = m.detect_all_anomalies(validators,preload = True)
    print("Załadowane serie:", len(m.loadedseries))
    for key, val_dict in anomalies.items():
        if any(val_dict[v] for v in val_dict):
            print(f"\nSeria: {key}")
            for validator_name, result in val_dict.items():
                if result:
                    print(f"  {validator_name}:")
                    for alert in result:
                        print(f"    - {alert}")