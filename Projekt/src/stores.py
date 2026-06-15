import json
import logging
from pathlib import Path
from file_security import check_readable, check_writable

logger = logging.getLogger(__name__)

DEFAULT_SELECTORS =[
    "[itemprop='price']",
    "meta[itemprop='price']",
    "#product_price",
    "#product-price",
    "[data-price]",
    ".product-price",
    ".price-box .price",
    ".offer-price",
    ".current-price",
    ".price-current",
    "span.price",
    ".price",
]

class StoreConfig:
    def __init__(self, name, domain, selector, currency = "PLN", notes = "", builtin = False):
        self.name = name
        self.domain = domain
        self.selector = selector
        self.currency = currency
        self.notes = notes
        self.builtin = builtin

    def matches_url_domain(self, url):
        return self.domain.lower() in url.lower()

    def to_dict(self):
        return {
            "name": self.name,
            "domain": self.domain,
            "selector": self.selector,
            "currency": self.currency,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d.get("name"),
            domain=d.get("domain"),
            selector=d.get("selector"),
            currency=d.get("currency", "PLN"),
            notes=d.get("notes", ""),
        )

#dodam wiecej potem bo trzeba sprawdzic ktore dzialaja
BUILTIN_STORES =[
    StoreConfig("Ceneo", "ceneo.pl", ".product-price .value, .price-box .price", builtin = True),
    StoreConfig("Amazon", "amazon.", "#corePriceDisplay_desktop_feature_div .a-price-whole, .apexPriceToPay .a-price-whole, #price_inside_buybox, .a-price .a-offscreen", builtin=True, currency="EUR"),
    StoreConfig("Books to Scrape", "books.toscrape.com", ".product_main .price_color", builtin=True, currency="GBP"),
    StoreConfig("Morele", "morele.net", ".product-price", builtin=True, currency="PLN"),
    StoreConfig("Oxylabs Sandbox", "sandbox.oxylabs.io", "div[class*='product-info-wrapper'] div[class*='price']", builtin=True, currency="EUR"),
    StoreConfig("localhost", "localhost:5000", "[data-price]", builtin=True, currency="PLN")
]

class StoreRegistry:
    def __init__(self, file_path = None):
        self.file_path = Path(file_path) if file_path else None
        self.builtin = {s.name: s for s in BUILTIN_STORES}
        self.custom = {}
        if file_path:
            self.load()

    def get_all(self):
        return list(self.builtin.values()) + list(self.custom.values())

    def get_names(self):
        return [s.name for s in self.get_all()]

    def get_by_name(self, name):
        return self.builtin.get(name) or self.custom.get(name)

    def is_custom(self, name):
        return name in self.custom

    def detect_store_from_url(self, url):
        for s in self.get_all():
            if s.matches_url_domain(url):
                return s
        return None


    def find_selector(self, html):
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html, "html.parser")
        price_re = re.compile(r"\b\d[\d\s]*[,.]\d{2}\b")

        for selector in DEFAULT_SELECTORS:
            el = soup.select_one(selector)
            if el:
                text = (
                    el.get("data-price") or el.get("content") or el.get_text(strip=True)
                )
                if text and price_re.search(text):
                    logger.info(f"Automatycznie wykryto selektor {selector}")
                    return selector
        return None


    def add_custom(self, store):
        store.builtin = False
        self.custom[store.name] = store
        self.save_to_json()

    def update_custom(self, store):
        store.builtin = False
        self.custom[store.name] = store
        self.save_to_json()

    def delete_custom(self, name):
        if name in self.custom:
            del self.custom[name]
            self.save_to_json()
            return True
        return False

    def load(self):
        if not self.file_path or not self.file_path.exists():
            return
        ok, msg = check_readable(self.file_path)
        if not ok:
            logger.error(msg)
            raise PermissionError(msg)
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            for item in data:
                s = StoreConfig.from_dict(item)
                self.custom[s.name] = s
            logger.info(f"Załadowano {len(self.custom)} sklepów z pliku {self.file_path}")
        except Exception as e:
            logger.error(f"Wystąpił błąd podczas ładowania sklepów z pliku: {e}")


    def save_to_json(self):
        if not self.file_path:
            return
        ok, msg = check_writable(self.file_path)
        if not ok:
            logger.error(msg)
            raise PermissionError(msg)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps([s.to_dict() for s in self.custom.values()], ensure_ascii=False, indent=2), encoding="utf-8")