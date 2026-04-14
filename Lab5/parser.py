import csv
import os


def parse_stacje(file_path):
    stations = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=",")

            for row in reader:
                station_data = {
                    "nr" : row.get("Nr"),
                    "kod" : row.get("Kod stacji"),
                    "kod_miedzynarodowy" : row.get("Kod międzynarodowy"),
                    "nazwa" : row.get("Nazwa stacji"),
                    "data_uruchomienia" : row.get("Data uruchomienia"),
                    "data_zamkniecia" : row.get("Data zamknięcia"),
                    "typ_stacji" : row.get("Typ stacji"),
                    "typ_obszaru" : row.get("Typ obszaru"),
                    "rodzaj_stacji" : row.get("Rodzaj stacji"),
                    "wojewodztwo" : row.get("Województwo"),
                    "miejscowosc" : row.get("Miejscowość"),
                    "adres" : row.get("Adres"),
                    "szerokosc_geo" : row.get("WGS84 φ N"),
                    "dlugosc_geo" : row.get("WGS84 λ E")
                }
                stations.append(station_data)

        return stations

    except FileNotFoundError:
        raise FileNotFoundError("Nie znaleziono pliku w podanej ścieżce")

def parse_measurements(catalog_path):
    measurements = []

    file_names = os.listdir(catalog_path)

    for file_name in file_names:
        file_path = os.path.join(catalog_path, file_name)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file, delimiter=",")
                rows = list(reader)

                if len(rows) < 7:
                    continue

                nr = rows[0]
                kod_stacji = rows[1]
                wskaznik = rows[2]
                czas = rows[3]
                jednostka = rows[4]
                kod_stanowiska = rows[5]
                wpisy = rows[6:]

                for wpis in wpisy:
                    if not wpis:
                        continue

                    data = wpis[0]
                    index = 1
                    for col in wpis[1:]:
                        try:
                            if col.strip():
                                value = float(col)
                            else:
                                value = None

                            measurements.append({"nr": index, "kod_stacji" : kod_stacji[index], "data" : data, "wartosc": value})

                        except ValueError:
                            index += 1
                            continue

                        index += 1
        except FileNotFoundError:
            print("Nie znaleziono pliku w podanej ścieżce")
            return []

    return measurements


if __name__ == "__main__":
    x = parse_stacje(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\stacje.csv")
  #  y = parse_measurements(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\measurements")
    pusta_linia_test = parse_stacje(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\empty_line_test.csv")

    print("Test pustej lini")
    print(pusta_linia_test[0])
    print(pusta_linia_test[1])

    print(f"Przykładowy wczytany słownik: {x[0]}")
    print()

    test1 = parse_stacje(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\empty")
   # test2 = parse_stacje("kfadshkfawuw")


