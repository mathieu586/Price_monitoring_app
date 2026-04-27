from datetime import datetime

from Lab6.validator import SeriesValidator, OutlierDetector, ZeroSpikeDetector, ThresholdDetector
from time_series import TimeSeries
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

        return [f"Info: {series.wskaznik}, at {series.kod} has mean = {statistics.mean(values)}"]


if __name__ == "__main__":
    time_series = TimeSeries("PM10", 2, 33, [datetime(1, 2, 3), datetime(1, 2, 4), datetime(1, 2, 5), datetime(1, 2, 3), datetime(1, 2, 4), datetime(1, 2, 5), datetime(1, 2, 3), datetime(1, 2, 4)], [1, 3, None, 0, None, 0, 200, 12], "g/m3")

    validators = [OutlierDetector(2), ZeroSpikeDetector(), ThresholdDetector(10), SimpleReporter()]

    for validator in validators:
        res = validator.analyze(time_series)
        print(res)