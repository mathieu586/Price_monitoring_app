from datetime import datetime

from Lab6.validator import SeriesValidator, OutlierDetector, ZeroSpikeDetector, ThresholdDetector
from zad1 import TimeSeries
import statistics
import validator

class SimpleReporter:
    def analyze(self, series: TimeSeries):
        values = []
        for wart in series.wartosci:
            if wart is not None:
                values.append(wart)

        if not values:
            return [f"Brak danych o pomiarach"]

        return [f"Info: {series.nazwa_wsk}, at {series.kod_stacji} has mean = {statistics.mean(values)}"]


if __name__ == "__main__":
    time_series = TimeSeries("wsk1", 2, 3, [datetime(1, 2, 3), datetime(1, 2, 4), datetime(1, 2, 5)], [1, 3, None], "g / m")

    validators = [OutlierDetector(2), ZeroSpikeDetector(), ThresholdDetector(3), SimpleReporter()]

    for validator in validators:
        res = validator.analyze(time_series)
        print(res)