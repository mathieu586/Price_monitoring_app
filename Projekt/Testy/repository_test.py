import pytest
import json
from pathlib import Path
from src.models import Product, PriceRecord, ProductStats
from src.repository import  JsonRepository, MemoryRepository

def make_product(pid = "abc1", name="Produkt test"):
    return Product(id=pid, name=name, url="https://example.com/produkt", store = "Test", selector=".price", check_interval=3600, alert_threshold=None)

def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class TestJsonRepo:
    def test_brak_pliku(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        assert repo.get_all_products() == []

    def test_ladowanie_z_pliku(self, tmp_path):
        path = tmp_path / "data.json"
        p = make_product()
        write_json(path, [p.to_dict()])
        repo = JsonRepository(path)
        assert len(repo.get_all_products()) == 1
        assert repo.get_product_by_id("abc1") is not None

    def test_wiele_produktow(self, tmp_path):
        path = tmp_path / "data.json"
        products = [make_product(pid=f"abc{i}", name=f"Produkt {i}") for i in range(10)]
        write_json(path, [p.to_dict() for p in products])
        repo = JsonRepository(path)
        assert len(repo.get_all_products()) == 10

    def test_pusty_plik(self, tmp_path):
        path = tmp_path / "data.json"
        path.write_text("", encoding="utf-8")
        repo = JsonRepository(path)
        assert repo.get_all_products() == []

    def test_nieprawidlowy_json(self, tmp_path):
        path = tmp_path / "data.json"
        path.write_text("{ to nie jest poprawny json", encoding="utf-8")
        repo = JsonRepository(path)
        assert repo.get_all_products() == []

    def test_plik_nie_lista(self, tmp_path):
        path = tmp_path / "data.json"
        write_json(path, {"products": []})
        repo = JsonRepository(path)
        assert repo.get_all_products() == []


    def test_zapisz_produkt(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        p = make_product()
        repo.save_product(p)
        assert repo.get_product_by_id("abc1") is not None

    def test_nadpisywanie_produktu(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        p = make_product()
        repo.save_product(p)
        p.name = "nowa nazwa"
        repo.save_product(p)
        assert repo.get_product_by_id("abc1").name == "nowa nazwa"
        assert len(repo.get_all_products()) == 1

    def test_get_nieistniejacy_produkt(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        assert repo.get_product_by_id("sadsadasdasd") is None

    def test_usuwanie_produktu(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        p = make_product()
        repo.save_product(p)
        result = repo.delete_product("abc1")
        assert result is True
        assert repo.get_product_by_id("abc1") is None

    def test_usuwanie_nieistniejacy(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        result = repo.delete_product("mmmm")
        assert result is False

    def test_zapisz_wiele_produktow(self, tmp_path):
        repo = JsonRepository(tmp_path / "data.json")
        p1 = make_product(pid="abc1", name="Produkt 1")
        p2 = make_product(pid="abc2", name="Produkt 2")
        p3 = make_product(pid="abc3", name="Produkt 3")
        repo.save_product(p1)
        repo.save_product(p2)
        repo.save_product(p3)
        assert len(repo.get_all_products()) == 3
        repo.delete_product("abc3")
        assert len(repo.get_all_products()) == 2
        assert repo.get_product_by_id("abc3") is None
