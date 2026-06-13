import logging
import re

import requests
from bs4 import BeautifulSoup

from Projekt.src.models import PriceRecord, Status, Product

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    def fetch_price(self, product):
        logger.info(f"Pobieranie ceny dla {product.name} ({product.url})")
        try:
            response = requests.get(product.url, headers=self.headers, timeout=10)

            if response.status_code == 403:
                return PriceRecord(price = 0.0, currency="PLN", status=Status.ERROR403, available=False)

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            element = soup.select_one(product.selector)

            if element:
                full_text = element.get("data-price") or element.get("content") or element.get_text(strip=True)
                full_text_upper = full_text.upper()

                currency = "PLN"
                if "$" in full_text_upper or "USD" in full_text_upper:
                    currency = "USD"
                elif "€" in full_text_upper or "EUR" in full_text_upper:
                    currency = "EUR"
                elif "£" in full_text_upper or "GBP" in full_text_upper:
                    currency = "GBP"

                no_space_text = full_text.replace(" ", "").replace("\u00A0", "")

                price_reg = re.search(r"(\d+[,.]\d{2}|\d+)", no_space_text)

                if price_reg:
                    full_price = price_reg.group(1)
                    clean_price = full_price.replace(",", ".")

                    return PriceRecord(float(clean_price), currency)
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd pobrania żądania dla produktu {product.url} : {e}")
            return PriceRecord(0.0, "PLN", status=Status.UNAVAILABLE, available=False)
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd dla produktu {product.url} : {e}")
            return PriceRecord(0.0, "PLN", status=Status.ERROR, available=False)
