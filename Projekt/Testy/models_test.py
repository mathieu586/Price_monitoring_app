import pytest
from src.models import PriceRecord, ProductStats, Product, Status

def make_record(price = 99.99, currency="PLN", status=Status.OK, available=True):
    return PriceRecord(price=price, currency=currency, status=status, available=available)

def make_product(alert_threshold = None, history = None):
    p = Product(id="abc1", name="Produkt testowy", url="https://example.com/produkt", store="Test", selector=".price",
                    check_interval=3600, alert_threshold=alert_threshold)
    if history:
        for record in history:
            p.price_history.append(record)
    return p

class TestPriceRecord:
    def test_poprawny_rekord(self):
        r = make_record()
        assert r.price == 99.99
        assert r.currency == "PLN"
        assert r.status == Status.OK
        assert r.available == True

    def test_cena_zero(self):
        r = make_record(price = 0)
        assert r.price == 0.0

    def test_cena_ujemna(self):
        with pytest.raises(ValueError):
            PriceRecord(price = -99.99, currency = "PLN")

    def test_cena_nie_jest_liczba(self):
        with pytest.raises(TypeError):
            PriceRecord(price = "nie liczba", currency = "PLN")

    def test_pusta_waluta(self):
        with pytest.raises(ValueError):
            PriceRecord(price = 99.99, currency = "")

    def test_dict_klucze(self):
        r = make_record()
        d = r.to_dict()
        assert set(d.keys()) == {"price", "currency", "status", "available", "timestamp"}


class TestProduct:
    def test_pierwszy_rekord_zmiana(self):
        p = make_product()
        r = make_record(price = 100.0)
        changed = p.add_price(r)
        assert changed is True
        assert len(p.price_history) == 1

    def test_taka_sama_cena_zmiana(self):
        p = make_product()
        r = make_record()
        p.add_price(r)
        changed = p.add_price(make_record())
        assert changed is False

    def test_inna_cena_zmiana(self):
        p = make_product()
        r = make_record()
        p.add_price(r)
        changed = p.add_price(make_record(price=200))
        assert changed is True

    def test_dodawanie_rekordu_taka_sama_cena(self):
        p = make_product()
        r = make_record()
        p.add_price(r)
        p.add_price(r)
        assert len(p.price_history) == 2

    def test_brak_historii(self):
        p = make_product()
        stats = p.get_stats()
        assert stats.current_price is None
        assert stats.best_price is None
        assert stats.avg_price is None
        assert stats.total_checks == 0

    def test_jeden_rekord(self):
        p = make_product(history=[make_record()])
        stats = p.get_stats()
        assert stats.current_price == 99.99
        assert stats.best_price == 99.99
        assert stats.avg_price == 99.99
        assert stats.total_checks == 1

    def test_wiele_rekordow(self):
        p = make_product(history=[make_record(100), make_record(80), make_record(60)])
        stats = p.get_stats()
        assert stats.current_price == 60
        assert stats.best_price == 60
        assert stats.avg_price == 80
        assert stats.total_checks == 3

    def test_statystyki_niedostepne_rekordy(self):
        p = make_product(history=[make_record(100), make_record(200), make_record(price=30, available=False)])
        stats = p.get_stats()
        assert stats.best_price == 100

    def test_statystyki_bledne_rekordy(self):
        p = make_product(history=[make_record(100), make_record(200), make_record(price=30, status=Status.ERROR)])
        stats = p.get_stats()
        assert stats.best_price == 100

    def test_cena_powyzej_progu(self):
        p = make_product(alert_threshold=80, history=[make_record(100)])
        assert p.check_if_alert() is False
    def test_cena_rowna_progowi(self):
        p = make_product(alert_threshold=80, history=[make_record(80)])
        assert p.check_if_alert() is True

    def test_cena_ponizej_progu(self):
        p = make_product(alert_threshold=80, history=[make_record(70)])
        assert p.check_if_alert() is True

    def test_niedostepny_produkt_prog(self):
        p = make_product(alert_threshold=800, history=[make_record(100,available=False)])
        assert p.check_if_alert() is False
