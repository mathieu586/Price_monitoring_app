import uuid
from datetime import datetime
from enum import Enum

class Status(Enum):
    OK = "ok"
    ERROR403 = "Error 403"
    NOT_FOUND = "Not found"
    UNAVAILABLE = "Unavailable"
    PENDING = "Pending"
    ERROR = "error"

class PriceRecord:
    def __init__(self, price, currency, status: Status = Status.OK , available = True, timestamp = None):
        if price < 0:
            raise ValueError("Cena nie może być ujemna")
        if not currency:
            raise ValueError("Brak waluty")
        self.price = price
        self.currency = currency
        self.available = available
        self.status = status
        self.timestamp = timestamp if timestamp is not None else datetime.now()

    def to_dict(self):
        return {
            "price": self.price,
            "currency": self.currency,
            "status": self.status.value,
            "available": self.available,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, d):
        status_raw = d.get("status", Status.OK.value)
        try:
            status = Status(status_raw)
        except ValueError:
            status = Status.ERROR

        return cls(price = d["price"],
                   currency = d["currency"],
                   status = status,
                   available = d.get("available", True),
                   timestamp = datetime.fromisoformat(d["timestamp"]),
                   )

    def __str__(self):
        return f"{self.price} {self.currency} ({self.status})"

    def __repr__(self):
        return f"{self.price} {self.currency} ({self.status})"

class ProductStats:
    def __init__(self, current_price, currency, best_price, worst_price, avg_price, change_percentage, total_checks, last_checked, last_status ):
        self.current_price = current_price
        self.currency = currency
        self.best_price = best_price
        self.worst_price = worst_price
        self.avg_price = avg_price
        self.change_percentage = change_percentage
        self.total_checks = total_checks
        self.last_checked = last_checked
        self.last_status = last_status

class Product:
    def __init__(self, id, name, url, store, selector, check_interval, alert_threshold, add_time = None, price_history = None):
        self.id = id
        self.name = name
        self.url = url
        self.store = store
        self.selector = selector
        self.add_time = add_time if add_time is not None else datetime.now()
        self.price_history = price_history if price_history is not None else []
        self.check_interval = check_interval
        self.alert_threshold = alert_threshold

    def add_price(self, price: PriceRecord):
        changed = False
        if not self.price_history or self.price_history[-1].price != price.price or self.price_history[-1].available != price.available:
            changed = True
        self.price_history.append(price)
        return changed

    def current_pricerecord(self):
        if not self.price_history:
            return None
        return self.price_history[-1]

    def get_stats(self):
        good_records = [record for record in self.price_history if record.available and record.status == Status.OK]
        prices = [record.price for record in good_records]

        current_record = self.current_pricerecord()
        current_price = current_record.price if current_record and current_record.available else None
        currency = current_record.currency if current_record else "PLN"
        change_percentage = None

        if len(good_records) >= 2:
            prev = good_records[-2].price
            cur = good_records[-1].price
            change_percentage = (((cur - prev) / prev) * 100) if prev else None

        best_price = min(prices) if prices else None
        worst_price = max(prices) if prices else None
        avg_price = sum(prices) / len(prices) if prices else None
        total_checks = len(self.price_history)
        last_checked = current_record.timestamp if current_record else None
        last_status = current_record.status if current_record else Status.PENDING

        return ProductStats(current_price, currency, best_price, worst_price, avg_price, change_percentage, total_checks, last_checked, last_status)

    def check_if_alert(self):
        record = self.current_pricerecord()
        if not self.alert_threshold or not record:
            return False
        return record.available and record.price <= self.alert_threshold

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "store": self.store,
            "selector": self.selector,
            "add_time": self.add_time.isoformat(),
            "price_history": [record.to_dict() for record in self.price_history],
            "check_interval": self.check_interval,
            "alert_threshold": self.alert_threshold,
        }

    @classmethod
    def from_dict(cls, d):
        product = cls(id = d["id"],
                      name = d["name"],
                      url = d["url"],
                      store = d["store"],
                      selector = d["selector"],
                      add_time = datetime.fromisoformat(d["add_time"]) if "add_time" in d else datetime.now(),
                      alert_threshold = d.get("alert_threshold"),
                      check_interval = d.get("check_interval"),
                      )
        for record in d.get("price_history", []):
            product.price_history.append(PriceRecord.from_dict(record))

        return product

    def get_table_row(self):
        stats = self.get_stats()

        return (
            self.name,
            self.store,
            f"{stats.current_price or 0.0} {stats.currency}",
            f"{stats.best_price or 0.0}",
            f"{stats.change_percentage or 0.0}%",
            f"{stats.avg_price or 0.0}",
            stats.total_checks,
            stats.last_status.value,
            stats.last_checked.strftime("%Y-%m-%d %H:%M") if stats.last_checked else "N/A"
        )

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())[:8]

    def __str__(self):
        last = self.price_history[-1] if self.price_history else None
        return f"Produkt {self.name}, url: {self.url}, cena: {last}"

    def __repr__(self):
        last = self.price_history[-1] if self.price_history else None
        return f"Produkt {self.name}, url: {self.url}, cena: {last}"