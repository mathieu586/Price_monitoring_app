import pytest
from bs4 import BeautifulSoup
from src.scraper import Scraper
from src.models import PriceRecord, Product, Status


class TestScraper:
    def test_pobieranie_ceny_bez_internetu(self):
        scraper = Scraper()

        html = '<div data-price="1 299,50 USD">1 299,50 $</div>'
        element = BeautifulSoup(html, "html.parser").find("div")

        result = scraper.extract_price_from_elem(element)

        assert result is not None
        price, currency = result
        assert price == 1299.50
        assert currency == "USD"

    def test_bledny_adres_strony(self):
        scraper = Scraper()
        p = Product(
            id="id_1",
            name="Zły Adres",
            url="https://strona-ktora-nie-istnieje-sfafafasdf.pl/produkt",
            store="TestStore",
            selector=".price",
            check_interval=1000,
            alert_threshold=10.0
        )

        record = scraper.fetch_price(p)

        assert isinstance(record, PriceRecord)
        assert record.status == Status.UNAVAILABLE
        assert record.available is False

    def test_pobieranie_z_dzialajacej_strony(self):
        scraper = Scraper()

        product = Product(
            id="test_id",
            name="Prawdziwy Test",
            url="https://www.ceneo.pl/167163125",
            store="Ceneo",
            selector=".product-price .value, .price-box .price",
            check_interval=1000,
            alert_threshold=200.0
        )

        record = scraper.fetch_price(product)

        assert isinstance(record, PriceRecord)
        assert record.status in [Status.OK, Status.NOT_FOUND]
        if record.status == Status.OK:
            assert record.price > 0.0