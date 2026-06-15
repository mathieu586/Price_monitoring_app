import time
import logging

from src.scraper import Scraper
from src.repository import MemoryRepository

logger = logging.getLogger(__name__)

class PriceMonitor:
    def __init__(self, repository, scraper):
        self.repository = repository
        self.scraper = scraper

    def check_product(self, product, notif_func=None):
        price = self.scraper.fetch_price(product)

        if price is None:
            logger.error(f"fetch_price zwróciło None dla {product.name}")
            return

        if product.add_price(price):
            self.repository.save_product(product)

            if product.check_if_alert():
                if notif_func:
                    notif_func(f"[ALERT] {product.name} spadł pod ustalony próg!")


    def check_all_products(self, notif_func=None):
        products = self.repository.get_all_products()

        for product in products:
            self.check_product(product, notif_func)
            time.sleep(3)