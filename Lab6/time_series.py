import datetime


class TimeSeries():
    def __init__(self, wskaznik, kod, czas, daty, wartosci, jednostka):
        self.wskaznik = wskaznik
        self.kod = kod
        self.czas = czas
        self.daty = daty
        self.wartosci = wartosci
        self.jednostka = jednostka

    def __str__(self):
        return f"Wskaźnik: {self.wskaznik}, kod: {self.kod}, czas uśredniania: {self.czas}"

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            daty = self.daty[key]
            wartosci = self.wartosci[key]
            if isinstance(key, int):
                return (daty, wartosci)
            return list(zip(daty, wartosci))

        if isinstance(key, (datetime.date, datetime.datetime)):
            if isinstance(key, datetime.datetime):
                date_key = key.date()
            else:
                date_key = key
            results = [(d, v) for d, v in zip(self.daty, self.wartosci) if d.date() == date_key]
            if not results:
                raise KeyError(f"Brak danych dla daty: {key}")
            if len(results) == 1:
                return results[0][1]
            return [v for _, v in results]

        raise KeyError("Niepoprawny klucz")

    @property
    def missing_count(self):
        c = 0
        for i in self.wartosci:
            if i == None:
                c+=1
        return c

    @property
    def completness(self):
        all = len(self.wartosci)
        notnone = all - self.missing_count
        return (notnone/all) * 100


if __name__ == "__main__":
    ts1 = TimeSeries("PM10", "AbcStacja1","24g", [datetime.datetime(2020, 1, 1, 12, 0, 0), datetime.datetime(2023, 11, 2), datetime.datetime(2025, 10, 2), datetime.datetime(2025, 10, 2)],
                     [1.55, 2.09, None, 2.00],"ng/m3")
    print(ts1[1])
    print(*(ts1[0:2]))
    print(ts1[datetime.datetime(2025, 10, 2)])
    print(ts1[datetime.date(2020, 1, 1)])
    print(ts1.missing_count)
    print(ts1.completness)