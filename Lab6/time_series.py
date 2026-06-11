import datetime
import statistics
from typing import Union, Optional, Tuple


class TimeSeries():
    def __init__(self, wskaznik: str, kod: str, czas: str, daty: list[datetime.datetime], wartosci: list[Optional[float]], jednostka: str) -> None:
        self.wskaznik: str = wskaznik
        self.kod: str = kod
        self.czas: str = czas
        self.daty: list[datetime.datetime] = daty
        self.wartosci: list[Optional[float]] = wartosci
        self.jednostka: str = jednostka

    def __str__(self) -> str:
        return f"Wskaźnik: {self.wskaznik}, kod: {self.kod}, czas uśredniania: {self.czas}"

    def __getitem__(self, key: Union[int, slice, datetime.datetime, datetime.date]) -> Union[Tuple[datetime.datetime, Optional[float]], list[Tuple[datetime.datetime, Optional[float]]], list[Optional[float]], Optional[float]]:
        if isinstance(key, int):
            return (self.daty[key], self.wartosci[key])

        if isinstance(key, slice):
            return list(zip(self.daty[key], self.wartosci[key]))

        if isinstance(key, (datetime.date, datetime.datetime)):
            date_key: datetime.date
            if isinstance(key, datetime.datetime):
                date_key = key.date()
            else:
                date_key = key
            results: list[Tuple[datetime.datetime, Optional[float]]] = [(d, v) for d, v in zip(self.daty, self.wartosci) if d.date() == date_key]
            if not results:
                raise KeyError(f"Brak danych dla daty: {key}")
            if len(results) == 1:
                return results[0][1]
            return [v for _, v in results]

        raise KeyError("Niepoprawny klucz")

    @property
    def missing_count(self) -> int:
        c: int = 0
        i: Optional[float]
        for i in self.wartosci:
            if i is None:
                c+=1
        return c

    @property
    def completness(self) -> float:
        all_count: int = len(self.wartosci)
        notnone: int = all_count - self.missing_count
        return (notnone/all_count) * 100

    @property
    def mean(self) -> float:
        cleared_data: list[float] = [v for v in self.wartosci if v is not None]
        return statistics.mean(cleared_data)

    @property
    def stddev(self) -> float:
        cleared_data: list[float] = [v for v in self.wartosci if v is not None]
        return statistics.stdev(cleared_data)


if __name__ == "__main__":
    ts1 = TimeSeries("PM10", "AbcStacja1","24g", [datetime.datetime(2020, 1, 1, 12, 0, 0), datetime.datetime(2023, 11, 2), datetime.datetime(2025, 10, 2), datetime.datetime(2025, 10, 2)],
                     [1.55, 2.09, None, 2.00],"ng/m3")
    print(ts1[1])
    print(ts1[0:2])
    print(ts1[datetime.datetime(2025, 10, 2)])
    print(ts1[datetime.date(2020, 1, 1)])
    print(ts1.missing_count)
    print(ts1.completness)