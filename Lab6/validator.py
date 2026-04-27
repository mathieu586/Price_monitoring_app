from abc import abstractmethod, ABC
from datetime import datetime

from time_series import TimeSeries
import statistics

class SeriesValidator(ABC):

    @abstractmethod
    def analyze(self, series: TimeSeries):
        pass

class OutlierDetector(SeriesValidator):
    def __init__(self, k=2):
        self.k = k

    def analyze(self, series: TimeSeries):
        alerts = []
        stat_wartosci = []

        for wart in series.wartosci:
            if wart is not None:
                stat_wartosci.append(wart)

        if len(stat_wartosci) < 2:
            return []

        stddev = statistics.stdev(stat_wartosci)
        mean = statistics.mean(stat_wartosci)

        i = 0
        for wartosc in series.wartosci:
            if wartosc is not None and abs(wartosc - mean) > self.k * stddev:
                alerts.append(f"[Outlier detector]Pomiar z dnia {series.daty[i]}, o wartości: {wartosc} przekroczył różnice {self.k} * odchylenie od średniej: {mean}")

            i += 1

        return alerts


class ZeroSpikeDetector(SeriesValidator):
    def analyze(self, series: TimeSeries):
        alerts = []
        no_data_counter = 0

        i = 0
        f = False
        last_missing_data_index = 0
        for wartosc in series.wartosci:
            if wartosc is None or wartosc == 0:
                no_data_counter += 1
                last_missing_data_index = i

                if no_data_counter >= 3:
                    f = True
            else:
                if f:
                    f = False
                    alerts.append(f"[Zero spike detector]Wykryto przynajmniej 3 zera lub 3 braki danych z rzędu, data ostatniego pomiaru z brakiem danych: {series.daty[last_missing_data_index]}")

                no_data_counter = 0

            i += 1

        if f:
            alerts.append(f"[Zero spike detector]Wykryto przynajmniej 3 zera lub 3 braki danych z rzędu, data ostatniego pomiaru z brakiem danych: {series.daty[last_missing_data_index]}")

        return alerts


class ThresholdDetector(SeriesValidator):
    def __init__(self, threshold):
        self.threshold = threshold

    def analyze(self, series: TimeSeries):
        alerts = []

        i = 0
        for wartosc in series.wartosci:
            if wartosc is not None and wartosc > self.threshold:
                alerts.append(f"[Threshold detector]Wykryto pomiar przekraczający zadany próg: {self.threshold}, wartość pomiaru: {wartosc}, data: {series.daty[i]}")

            i += 1

        return alerts

if __name__ == "__main__":
    time_series = TimeSeries("PM10", 2, 33, [datetime(1, 2, 3), datetime(1, 2, 4), datetime(1, 2, 5), datetime(1, 2, 3), datetime(1, 2, 4), datetime(1, 2, 5), datetime(1, 2, 3), datetime(1, 2, 4)], [1, 3, None, 0, None, 0, 200, 12], "g/m3")
    time_series2 = TimeSeries("PM10", 3, 13, [datetime(1, 2, 4), datetime(1, 2, 5), datetime(1, 2, 3)], [1, 6, 10], "g/m3")

    detector1 = OutlierDetector(2)
    detector2 = ZeroSpikeDetector()
    detector3 = ThresholdDetector(10)

    print(detector1.analyze(time_series))
    print(detector2.analyze(time_series))
    print(detector3.analyze(time_series))

    print(detector1.analyze(time_series2))
    print(detector2.analyze(time_series2))
    print(detector3.analyze(time_series2))