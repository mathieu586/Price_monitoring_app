import time

from scraper import Scraper
from repository import MemoryRepository

class PriceMonitor:
    def __init__(self, repository, scraper):
        self.repository = repository
        self.scraper = scraper

    def check_product(self, product):
        price = self.scraper.fetch_price(product)

        if product.add_price(price):
            self.repository.save_product(product)

            if product.check_if_alert():
                print("Powiadomienie!")  # DO ZMIANY -----------------------------------

    def check_all_products(self):
        products = self.repository.get_all_products()

        for product in products:
            self.check_product(product)
            time.sleep(2)