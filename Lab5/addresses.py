import re
import csv
from pathlib import Path
from parser import parse_stacje

def get_addresses(path, city):
    if not isinstance(path, Path):
        path = Path(path)
    addr_pattern = re.compile(r'^(?P<ulica>.+?)\s+(?P<numer>\d+[A-Za-z]?(/\d+[A-Za-z]?)?)$')
    result = []
    if not path.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {path}")

    if path.is_dir():
        raise ValueError(f"Podano katalog zamiast pliku CSV: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Plik musi być CSV: {path}")


    stations = parse_stacje(path)
    for row in stations:
        miejscowosc = (row.get("miejscowosc") or "").strip()
        if miejscowosc.lower() != city.lower():
            continue

        woj = (row.get("wojewodztwo") or "").strip()
        adr = (row.get("adres") or "").strip()

        m = addr_pattern.match(adr)
        if m:
            ulica = m.group("ulica").strip() if m.group("ulica") else adr
            numer = m.group("numer") or None
        else:
            ulica = adr
            numer = None
        result.append((woj, miejscowosc, ulica, numer))

    return result

if __name__ == "__main__" :
    print(get_addresses(r"C:\Users\kubap\PycharmProjects\PythonProject8\Lab5\stacje.csv", "Warszawa"))
    print(get_addresses(r"C:\Users\kubap\PycharmProjects\PythonProject8\Lab5\stacje.csv", ""))
    #print(get_addresses(r"C:\Users\kubap\PycharmProjects\PythonProject8\Lab5\zlyplik.csv", "Warszawa"))
