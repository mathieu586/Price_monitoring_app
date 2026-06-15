import pytest
import json
from pathlib import Path
from src.stores import StoreConfig, StoreRegistry

def make_store(name="SklepTestowy", domain="test.pl", builtin=False):
    return StoreConfig(name=name, domain=domain, selector=".cena", currency="PLN", notes="", builtin=builtin)

def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class TestStoreConfig:
    def test_to_dict(self):
        s = make_store()
        d = s.to_dict()
        assert d["name"] == "SklepTestowy"
        assert d["domain"] == "test.pl"
        assert d["currency"] == "PLN"

    def test_from_dict(self):
        d = {
            "name": "SklepTestowy",
            "domain": "test.pl",
            "selector": ".price",
            "currency": "USD",
            "notes": "test",
            "builtin": False
        }
        s = StoreConfig.from_dict(d)
        assert s.name == "SklepTestowy"
        assert s.domain == "test.pl"
        assert s.currency == "USD"

class TestStoreRegistry:
    def test_pusty_rejestr(self, tmp_path):
        repo = StoreRegistry(tmp_path / "stores.json")
        assert len(repo.custom) == 0

    def test_ladowanie_z_pliku(self, tmp_path):
        path = tmp_path / "stores.json"
        s = make_store()
        write_json(path, [s.to_dict()])

        repo = StoreRegistry(path)
        loaded = repo.get_by_name("SklepTestowy")
        assert loaded is not None
        assert loaded.domain == "test.pl"

    def test_dodawanie_sklepu(self, tmp_path):
        repo = StoreRegistry(tmp_path / "stores.json")
        s = make_store(name="NowySklep")

        repo.add_custom(s)
        assert repo.get_by_name("NowySklep") is not None

    def test_aktualizacja_sklepu(self, tmp_path):
        repo = StoreRegistry(tmp_path / "stores.json")
        repo.add_custom(make_store(name="SklepDoZmiany", domain="test.pl"))

        sklep = repo.get_by_name("SklepDoZmiany")
        sklep.domain = "nowadomena.pl"

        repo.update_custom(sklep)

        updated = repo.get_by_name("SklepDoZmiany")
        assert updated.domain == "nowadomena.pl"

    def test_usuwanie_sklepu(self, tmp_path):
        repo = StoreRegistry(tmp_path / "stores.json")
        repo.add_custom(make_store("SklepDoUsun"))

        result = repo.delete_custom("SklepDoUsun")

        assert result is True
        assert repo.get_by_name("SklepDoUsun") is None

    def test_usuwanie_nieistniejacego(self, tmp_path):
        repo = StoreRegistry(tmp_path / "stores.json")

        result = repo.delete_custom("NieistniejacySklep")

        assert result is False

    def test_wykrywanie_url(self, tmp_path):
        repo = StoreRegistry(tmp_path / "stores.json")
        repo.add_custom(make_store(name="Sklep A", domain="sklepa.pl"))
        repo.add_custom(make_store(name="Sklep B", domain="sklepb.com"))

        sklep1 = repo.detect_store_from_url("https://www.sklepa.pl/produkt/79324")
        assert sklep1 is not None
        assert sklep1.name == "Sklep A"

        sklep2 = repo.detect_store_from_url("http://sklepb.com/item")
        assert sklep2 is not None
        assert sklep2.name == "Sklep B"

        sklep3 = repo.detect_store_from_url("https://inny-sklep.pl/produkt")
        assert sklep3 is None
