import logging
import re

import requests
from bs4 import BeautifulSoup

from Projekt.src.models import PriceRecord, Status, Product
from Projekt.src.stores import DEFAULT_SELECTORS

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def extract_price_from_elem(self, element):
        full_text = element.get("data-price") or element.get("content") or element.get_text(strip=True)
        if not full_text:
            logger.warning("Znaleziony element jest pusty")
            return PriceRecord(price=0.0, currency="PLN", status=Status.ERROR, available=False)
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

        if not price_reg:
            logger.warning(f"Nie wykryto ceny w tekście '{full_text}")
            return PriceRecord(price=0.0, currency="PLN", status=Status.ERROR, available=False)
        full_price = price_reg.group(1)
        clean_price = float(full_price.replace(",", "."))

        return clean_price, currency

    def fetch_price(self, product):
        logger.info(f"Pobieranie ceny dla {product.name} ({product.url})")
        try:
            response = requests.get(product.url, headers=self.headers, timeout=10)

            if response.status_code == 403:
                return PriceRecord(price = 0.0, currency="PLN", status=Status.ERROR403, available=False)

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            if product.selector:
                element = soup.select_one(product.selector)
                if not element:
                    logger.warning(f"Nie znaleziono elementu dla selektora '{product.selector}'")
                    return PriceRecord(price = 0.0, currency="PLN", status=Status.NOT_FOUND, available=False)

                result = self.extract_price_from_elem(element)
                if not result:
                    logger.warning(f"Nie wykryto ceny w elemencie")
                    return PriceRecord(price = 0.0, currency="PLN", status=Status.ERROR, available=False)

                price, currency = result
                return PriceRecord(price, currency)

            logger.info(f"Brak selektora dla {product.name}, używane domyślne selektory")
            for selector in DEFAULT_SELECTORS:
                element = soup.select_one(selector)
                if not element:
                    continue
                result = self.extract_price_from_elem(element)
                if result:
                    price, currency = result
                    logger.info(f"Znaleziono cenę przy użyciu domyślnego selektora {selector}.")
                    return PriceRecord(price, currency)

            logger.warning(f"Żaden domyślny selektor nie dopasował ceny")
            return PriceRecord(price = 0.0, currency="PLN", status=Status.NOT_FOUND, available=False)

        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd pobrania żądania dla produktu {product.url} : {e}")
            return PriceRecord(0.0, "PLN", status=Status.UNAVAILABLE, available=False)
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd dla produktu {product.url} : {e}")
            return PriceRecord(0.0, "PLN", status=Status.ERROR, available=False)
