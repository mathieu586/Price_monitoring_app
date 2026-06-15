import time
from src.monitor import PriceMonitor
from src.models import Product, PriceRecord, Status


class FakeScraper:
    def __init__(self, price_to_return):
        self.price_to_return = price_to_return

    def fetch_price(self, product):
        return self.price_to_return


class FakeRepository:
    def __init__(self):
        self.saved_products = []

    def save_product(self, product):
        self.saved_products.append(product)

    def get_all_products(self):
        return self.saved_products

class TestPriceMonitor:
    def test_scraper_zwraca_none(self):
        scraper = FakeScraper(price_to_return=None)
        repo = FakeRepository()
        monitor = PriceMonitor(repo, scraper)

        prod = Product("1", "Odkurzacz", "url", "Sklep", ".price", 1000, 50.0)

        monitor.check_product(prod)

        assert len(repo.saved_products) == 0

    def test_cena_bez_zmian(self):
        scraper = FakeScraper(price_to_return=None)
        repo = FakeRepository()
        monitor = PriceMonitor(repo, scraper)

        prod = Product("1", "Odkurzacz", "url", "Sklep", ".price", 1000, 50.0)

        prod.add_price = lambda x: False

        monitor.check_product(prod)

        assert len(repo.saved_products) == 0

    def test_cena_sie_zmienia_brak_alertu(self):
        scraper = FakeScraper(price_to_return=100.0)
        repo = FakeRepository()
        monitor = PriceMonitor(repo, scraper)

        prod = Product("1", "Odkurzacz", "url", "Sklep", ".price", 1000, 50.0)

        prod.add_price = lambda x: True
        prod.check_if_alert = lambda: False

        monitor.check_product(prod)

        assert len(repo.saved_products) == 1
        assert repo.saved_products[0].name == "Odkurzacz"

    def test_cena_sie_zmienia_wywolanie_alertu(self):
        scraper = FakeScraper(price_to_return=100.0)
        repo = FakeRepository()
        monitor = PriceMonitor(repo, scraper)

        prod = Product("1", "Odkurzacz", "url", "Sklep", ".price", 1000, 50.0)

        prod.add_price = lambda x: True
        prod.check_if_alert = lambda: True

        monitor.check_product(prod)

        assert len(repo.saved_products) == 1
        assert repo.saved_products[0].name == "Odkurzacz"

    def test_sprawdzania_wszystkich_produktow_w_petli(self):
        scraper = FakeScraper(price_to_return=None)
        repo = FakeRepository()
        monitor = PriceMonitor(repo, scraper)

        prod1 = Product("1", "Odkurzacz", "url", "Sklep", ".price", 1000, 50.0)
        prod2 = Product("2", "Telefon", "url", "Sklep", ".price", 1000, 50.0)

        repo.saved_products.append(prod1)
        repo.saved_products.append(prod2)

        check_count = 0
        def fake_check(product, notif_func=None):
            nonlocal check_count
            check_count += 1

        monitor.check_product = fake_check

        monitor.check_all_products()

        assert check_count == 2



