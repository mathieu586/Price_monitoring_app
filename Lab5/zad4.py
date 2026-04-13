import re
from parser import parse_stacje
from pathlib import Path

def analyze_stations(path):
    if not isinstance(path, Path):
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {path}")

    if path.is_dir():
        raise ValueError(f"Podano katalog zamiast pliku CSV: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Plik musi być CSV: {path}")

    stations = parse_stacje(path)
    results = {
        "dates": [],
        "cords": [],
        "myslnik_names": [],
        "normalized_names": [],
        "mob_errors": [],
        "triple_locations": [],
        "street_locations": []
    }
    date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
    cord_pattern = re.compile(r"\b\d+\.\d{6}\b")
    myslnik_pattern = re.compile(r".+ - (?![Mm]obil).+")
    triple_pattern = re.compile(r".+ - .+ - (?![Mm]obil).+")
    street_pattern = re.compile(r"\b(ul\.|al\.)\s+[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\s]+,\s*[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\s]+", re.IGNORECASE)

    for s in stations:
        for f in ["data_uruchomienia", "data_zamkniecia"]:
            value = s.get(f)
            if value:
                results["dates"].extend(date_pattern.findall(value))
        szerokosc = s.get("szerokosc_geo")
        dlugosc = s.get("dlugosc_geo")

        if szerokosc and dlugosc:
            if cord_pattern.match(szerokosc) and cord_pattern.match(dlugosc):
                results["cords"].append((szerokosc,dlugosc))

        name = s.get("nazwa") or ""
        if myslnik_pattern.match(name):
            results["myslnik_names"].append(name)

        norm = re.sub(r"\s+", "_", name)
        norm = re.sub(r"[ąćęłńóśźż]", lambda m: {
            "ą": "a", "ć": "c", "ę": "e", "ł": "l",
            "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z"
        }[m.group()], norm)
        results["normalized_names"].append(norm)

        kod = s.get("kod") or ""
        rodzaj = (s.get("rodzaj_stacji") or "").lower()

        if re.search(r"MOB$", kod) and not re.search(r"mobilna", rodzaj, re.IGNORECASE):
            results["mob_errors"].append(kod)

        if triple_pattern.match(name):
            results["triple_locations"].append(name)
        adr = s.get("adres") or ""
        if street_pattern.search(adr):
            results["street_locations"].append(adr)

    return results

if __name__ == "__main__":
    data = analyze_stations(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\stacje.csv")
    print("Daty: ", data["dates"][:10])
    print("Współrzędne:", data["cords"][:10])
    print("Nazwy z myślnikiem:", data["myslnik_names"][:10])
    print("Błędy MOB:", data["mob_errors"])
    print("3 człony:", data["triple_locations"][:10])
    print("ul./al.:", data["street_locations"][:10])

    print()
    data2 =  analyze_stations(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\pusty.csv")
    print("Daty: ", data2["dates"][:10])
    print("Współrzędne:", data2["cords"][:10])
    print("Nazwy z myślnikiem:", data2["myslnik_names"][:10])
    print("Błędy MOB:", data2["mob_errors"])
    print("3 człony:", data2["triple_locations"][:10])
    print("ul./al.:", data2["street_locations"][:10])
