from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)
#UŻYCIE: localhost:5000
PRODUKTY_BAZA = [
    {"id": 1,  "nazwa": "Laptop ProBook 15",      "kategoria": "Elektronika",  "cena_baza": 3499.00, "img": "💻"},
    {"id": 2,  "nazwa": "Mysz bezprzewodowa X200", "kategoria": "Elektronika",  "cena_baza": 129.00,  "img": "🖱️"},
    {"id": 3,  "nazwa": "Monitor 27\" 4K",         "kategoria": "Elektronika",  "cena_baza": 1899.00, "img": "🖥️"},
    {"id": 4,  "nazwa": "Klawiatura mechaniczna",  "kategoria": "Elektronika",  "cena_baza": 299.00,  "img": "⌨️"},
    {"id": 5,  "nazwa": "Słuchawki Studio Pro",    "kategoria": "Audio",        "cena_baza": 549.00,  "img": "🎧"},
    {"id": 6,  "nazwa": "Głośnik Bluetooth Mini",  "kategoria": "Audio",        "cena_baza": 199.00,  "img": "🔊"},
    {"id": 7,  "nazwa": "Mikrofon USB Kondensator","kategoria": "Audio",        "cena_baza": 379.00,  "img": "🎙️"},
    {"id": 8,  "nazwa": "Smartwatch Fit X3",       "kategoria": "Gadżety",      "cena_baza": 699.00,  "img": "⌚"},
    {"id": 9,  "nazwa": "Powerbank 20000mAh",      "kategoria": "Gadżety",      "cena_baza": 149.00,  "img": "🔋"},
    {"id": 10, "nazwa": "Kabel USB-C 2m Premium",  "kategoria": "Gadżety",      "cena_baza": 49.00,   "img": "🔌"},
    {"id": 11, "nazwa": "Tablet 10\" 128GB",        "kategoria": "Elektronika",  "cena_baza": 1299.00, "img": "📱"},
    {"id": 12, "nazwa": "Kamera internetowa FHD",  "kategoria": "Elektronika",  "cena_baza": 249.00,  "img": "📷"},
]

def losuj_cene(cena_baza):
    """Losuje cenę w zakresie ±30% od ceny bazowej."""
    wspolczynnik = random.uniform(0.70, 1.30)
    cena = round(cena_baza * wspolczynnik, 2)
    # Zaokrąglij do .99 losowo
    if random.random() > 0.5:
        cena = round(cena) - 0.01
    return max(cena, 0.99)

def generuj_produkty():
    produkty = []
    for p in PRODUKTY_BAZA:
        cena = losuj_cene(p["cena_baza"])
        zmiana = round(((cena - p["cena_baza"]) / p["cena_baza"]) * 100, 1)
        produkty.append({
            "id": p["id"],
            "nazwa": p["nazwa"],
            "kategoria": p["kategoria"],
            "cena": cena,
            "cena_baza": p["cena_baza"],
            "zmiana_procent": zmiana,
            "img": p["img"],
            "dostepnosc": random.choice(["Dostępny", "Dostępny", "Dostępny", "Mało sztuk", "Niedostępny"]),
            "ocena": round(random.uniform(3.0, 5.0), 1),
            "ilosc_opinii": random.randint(5, 1200),
            "timestamp": int(time.time()),
        })
    return produkty

@app.route("/")
def index():
    produkty = generuj_produkty()
    kategorie = sorted(set(p["kategoria"] for p in PRODUKTY_BAZA))
    return render_template("index.html", produkty=produkty, kategorie=kategorie)

@app.route("/api/produkty")
def api_produkty():
    """JSON endpoint do scrapowania programistycznego."""
    produkty = generuj_produkty()
    return jsonify({
        "timestamp": int(time.time()),
        "ilosc": len(produkty),
        "produkty": produkty
    })

@app.route("/api/produkt/<int:produkt_id>")
def api_produkt(produkt_id):
    """JSON endpoint dla pojedynczego produktu."""
    baza = next((p for p in PRODUKTY_BAZA if p["id"] == produkt_id), None)
    if not baza:
        return jsonify({"error": "Produkt nie znaleziony"}), 404
    cena = losuj_cene(baza["cena_baza"])
    zmiana = round(((cena - baza["cena_baza"]) / baza["cena_baza"]) * 100, 1)
    return jsonify({
        "id": baza["id"],
        "nazwa": baza["nazwa"],
        "kategoria": baza["kategoria"],
        "cena": cena,
        "cena_baza": baza["cena_baza"],
        "zmiana_procent": zmiana,
        "img": baza["img"],
        "dostepnosc": random.choice(["Dostępny", "Dostępny", "Mało sztuk", "Niedostępny"]),
        "timestamp": int(time.time()),
    })

@app.route("/produkt/<int:produkt_id>")
def produkt(produkt_id):
    baza = next((p for p in PRODUKTY_BAZA if p["id"] == produkt_id), None)
    if not baza:
        return "Nie znaleziono", 404
    cena = losuj_cene(baza["cena_baza"])
    zmiana = round(((cena - baza["cena_baza"]) / baza["cena_baza"]) * 100, 1)
    p = {
        "id": baza["id"],
        "nazwa": baza["nazwa"],
        "kategoria": baza["kategoria"],
        "cena": cena,
        "cena_baza": baza["cena_baza"],
        "zmiana_procent": zmiana,
        "img": baza["img"],
        "dostepnosc": random.choice(["Dostępny", "Dostępny", "Mało sztuk", "Niedostępny"]),
        "ocena": round(random.uniform(3.0, 5.0), 1),
        "ilosc_opinii": random.randint(5, 1200),
        "timestamp": int(time.time()),
    }
    return render_template("produkt.html", p=p)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
