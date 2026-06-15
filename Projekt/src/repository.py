import json
import logging
from abc import ABC, abstractmethod
from models import Product
from pathlib import Path
from file_security import check_readable, check_writable

logger = logging.getLogger(__name__)

class ProductRepository(ABC):
    @abstractmethod
    def get_all_products(self): ...
    @abstractmethod
    def get_product_by_id(self, product_id): ...
    @abstractmethod
    def save_product(self, product): ...
    @abstractmethod
    def delete_product(self, product_id): ...

class JsonRepository(ProductRepository):
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.cache = {}
        self.load()

    def load(self):
        if not self.path.exists():
            return
        ok, msg = check_readable(self.path)
        if not ok:
            logger.error(msg)
            raise PermissionError(msg)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for item in data:
                p = Product.from_dict(item)
                self.cache[p.id] = p
            logger.info(f"Załadowano {len(self.cache)} produktów")
        except Exception as e:
            logger.error(f"Wystąpił błąd przy ładowaniu produktów: {e}")

    def save_to_json(self):
        ok, msg = check_writable(self.path)
        if not ok:
            logger.error(msg)
            raise PermissionError(msg)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([p.to_dict() for p in self.cache.values()], ensure_ascii=False, indent=2), encoding="utf-8")

    def get_all_products(self):
        return list(self.cache.values())

    def get_product_by_id(self, product_id):
        return self.cache.get(product_id)

    def save_product(self, product):
        self.cache[product.id] = product
        self.save_to_json()

    def delete_product(self, product_id):
        if product_id in self.cache:
            del self.cache[product_id]
            self.save_to_json()
            return True
        return False

class MemoryRepository(ProductRepository):
    def __init__(self):
        self.store = {}

    def get_all_products(self):
        return list(self.store.values())

    def get_product_by_id(self, product_id):
        return self.store.get(product_id)

    def save_product(self, product):
        self.store[product.id] = product

    def delete_product(self, product_id):
        if product_id in self.store:
            del self.store[product_id]
            return True
        return False