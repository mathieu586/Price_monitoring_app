from Lab6.time_series import TimeSeries
import datetime
import pytest
from Lab6.validator import OutlierDetector, ZeroSpikeDetector, ThresholdDetector

@pytest.fixture()
def test_time_series():
    dates = [datetime.datetime(2020, 1, 1, 12, 0, 0), datetime.datetime(2023, 11, 2), datetime.datetime(2025, 10, 2), datetime.datetime(2025, 10, 2)]
    values = [1.55, 2.09, None, 2.00]

    return TimeSeries("PM10", "AbcStacja1", "24g", dates, values, "ng/m3")

def test_integer_getitem(test_time_series):
    expected = (datetime.datetime(2025, 10, 2), None)

    assert test_time_series[2] == expected

def test_slice_getitem(test_time_series):
    expected = [(datetime.datetime(2020, 1, 1, 12, 0, 0), 1.55), (datetime.datetime(2023, 11, 2), 2.09)]

    assert test_time_series[0:2] == expected

def test_date_getitem(test_time_series):
    date = datetime.date(2023, 11, 2)
    expected = 2.09

    assert test_time_series[date] == expected

def test_absent_date_getitem(test_time_series):
    date = datetime.date(2018, 11, 2)

    with pytest.raises(KeyError):
        e = test_time_series[date]


def test_mean_and_stddev():
    dates = [datetime.datetime(2023, 11, 2), datetime.datetime(2025, 10, 2), datetime.datetime(2025, 10, 2)]
    values = [2.0, 4.0, 6.0]

    ts = TimeSeries("PM10", "AbcStacja1","24g", dates, values,"ng/m3")

    expected_mean = 4.0
    expected_stddev = 2.0


    assert expected_mean == ts.mean
    assert expected_stddev == ts.stddev


def test_mean_and_stddev_with_none():
    dates = [datetime.datetime(2023, 11, 2), datetime.datetime(2025, 10, 2), datetime.datetime(2025, 10, 2), datetime.datetime(2025, 10, 3)]
    values = [2.0, 4.0, 6.0, None]

    ts = TimeSeries("PM10", "AbcStacja2","24g", dates, values,"ng/m3")

    expected_mean = 4.0
    expected_stddev = 2.0


    assert expected_mean == ts.mean
    assert expected_stddev == ts.stddev


def test_outlier():
    ts = TimeSeries("PM10", "AbcStacja1", "24g", [datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4), datetime.datetime(1, 2, 5), datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4), datetime.datetime(1, 2, 5), datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4)], [1, 3, None, 0, None, 0, 200, 12], "g/m3")
    detector = OutlierDetector(2)
    alerts = detector.analyze(ts)

    assert len(alerts) == 1
    assert "200" in alerts[0]


def test_zero_spike():
    ts = TimeSeries("PM10", "AbcStacja1", "24g", [datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4), datetime.datetime(1, 2, 5), datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4), datetime.datetime(1, 2, 5), datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4)], [1, 3, None, 0, None, 0, 200, 12], "g/m3")
    detector = ZeroSpikeDetector()
    alerts = detector.analyze(ts)

    assert len(alerts) == 1
    assert "0001-02-05 00:00:00" in alerts[0]

def test_threshold():
    ts = TimeSeries("PM10", "AbcStacja1", "24g", [datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4), datetime.datetime(1, 2, 5), datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4), datetime.datetime(1, 2, 5), datetime.datetime(1, 2, 3), datetime.datetime(1, 2, 4)], [1, 3, None, 0, None, 0, 200, 12], "g/m3")
    detector = ThresholdDetector(10)
    alerts = detector.analyze(ts)

    assert len(alerts) == 2
    assert "wartość pomiaru: 200" in alerts[0]
    assert "wartość pomiaru: 12" in alerts[1]


