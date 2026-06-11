import datetime


class Station:
    def __init__(self, kod: int, nazwa: str, data_uruchomienia:datetime.datetime, data_zamkniecia:datetime.datetime, typ_stacji:int, rodzaj_stacji:str, miejscowosc:str, szerokosc_geo:int, dlugosc_geo:int) -> None:
        self.kod = kod
        self.nazwa = nazwa
        self.data_uruchomienia = data_uruchomienia
        self.data_zamkniecia = data_zamkniecia
        self.typ_stacji = typ_stacji
        self.rodzaj_stacji = rodzaj_stacji
        self.miejscowosc = miejscowosc
        self.szerokosc_geo = szerokosc_geo
        self.dlugosc_geo = dlugosc_geo


    def __str__(self) -> str:
        return f"kod: {self.kod}, nazwa: {self.nazwa}, data uruchomienia: {self.data_uruchomienia}"

    def __repr__(self) -> str:
        return f"code: {self.kod}, name: {self.nazwa}, {self.data_uruchomienia}, {self.data_zamkniecia}, {self.rodzaj_stacji}, {self.miejscowosc}"

    def __eq__(self, other) -> bool:
        return self.kod == other.kod



class TimeSeries:
    def __init__(self, nazwa_wsk:str, kod_stacji:int, czas_usr:int, daty_pomiaru:list[datetime.datetime], wartosci:list[float], jednostka:str) -> None:
        self.nazwa_wsk = nazwa_wsk
        self.kod_stacji = kod_stacji
        self.czas_usr = czas_usr
        self.daty_pomiaru = daty_pomiaru
        self.wartosci = wartosci
        self.jednostka = jednostka

    def __str__(self) -> str:
        return f"nazwa wskaźnika: {self.nazwa_wsk}, ...."

    def __repr__(self) -> str:
        return f"name: {self.nazwa_wsk}, code: {self.kod_stacji}, {self.czas_usr}, {self.daty_pomiaru}, {self.wartosci}, {self.jednostka}"

    def __getitem__(self, index: int) -> tuple[datetime.datetime, float]:
        date = self.daty_pomiaru[index]
        val = self.wartosci[index]


        if isinstance(index, slice):
            res = []
            for i in range(slice.start, slice.stop):
                res.append((self.daty_pomiaru[i]), self.wartosci[i])
            return res
        else:

            return (date, val)

    def __getitem1__(self, date:datetime.datetime) -> list[float]:
        if isinstance(date, datetime.datetime):
            res = []
            for i in range(0, len(self.daty_pomiaru)):
                try:
                    if self.daty_pomiaru[i] == date:
                        res.append(wartosci[i])
                except ValueError:
                    continue

            return res
        elif isinstance(date, datetime.date):
            res = []
            for i in range(0, len(self.daty_pomiaru)):
                try:
                    if self.daty_pomiaru[i].date() == date:
                        res.append(wartosci[i])
                except ValueError:
                    continue

            return res
        else:
            raise KeyError("Argument musi być typu datetime.date lub datetime.datetime")


    @property
    def missing_count(self) -> int:
        counter = 0
        for pom in self.wartosci:
            if not pom:
                counter += 1

        return counter

    @property
    def completeness(self) -> float:
        all_count = len(self.daty_pomiaru)
        correct_count = all_count - self.missing_count

        if not all_count == 0:
            return (correct_count / all_count) * 100
        else:
            return 0


if __name__ == "__main__":
    station1 = Station(123, "Stacja1", datetime.date(2020, 3, 23), datetime.date(2022, 3, 23), "pogodowa", "duża", "Wrocław", 1, 1)
    print(station1.__str__())
    print(station1.__repr__())

    station2 = Station(124, "Stacja2", datetime.date(2019, 2, 23), datetime.date(2022, 3, 23), "pogodowa", "duża", "Wrocław", 1, 1)
    station3 = Station(123, "Stacja3", datetime.date(2018, 3, 23), datetime.date(2022, 3, 23), "pogodowa", "duża", "Wrocław", 1, 1)


    print(f"Czy takie same: {station1 == station2}")
    print(f"Czy takie same: {station1 == station3}")

    print("=================== TESTY TIMESERIES ===================")
    daty = []
    daty.append(datetime.datetime(2020, 3, 4))
    daty.append(datetime.datetime(2020, 2, 1))
    daty.append(datetime.datetime(2020, 2, 1))
    daty.append(datetime.datetime(2020, 2, 1))
    daty.append(datetime.datetime(2020, 6, 3))

    wartosci = []
    wartosci.append(2.4)
    wartosci.append(2.6)
    wartosci.append(None)
    wartosci.append(0.5)
    wartosci.append(None)

    time_series_1 = TimeSeries("wsk1", 12, 10, daty, wartosci, "g/m")
    print(time_series_1.__str__())
    print(time_series_1.__repr__())
    print(time_series_1.__getitem__(1))

    print(time_series_1.__getitem1__(datetime.datetime(2020, 2, 1)))
    print(time_series_1.__getitem1__(datetime.date(2020, 2, 1)))


    print(f"missing count: {time_series_1.missing_count}")
    print(f"completeness: {time_series_1.completeness}%")









