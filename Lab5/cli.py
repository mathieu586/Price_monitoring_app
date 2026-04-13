import argparse
import datetime
import statistics
from group_measurement import group_measurement_files_by_key
from parser import parse_stacje
import csv
import random
import logging
import sys


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level

def setup_logging():
    logger = logging.getLogger("cli")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(MaxLevelFilter(logging.WARNING))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger

logger = setup_logging()

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        logger.error(f"Błąd argumentów: {message}")
        self.print_usage(sys.stderr)
        sys.exit(2)

def parse():
    parser = ArgumentParser(description="command line interface")
    parser.add_argument("--wielkosc", required=True, type=str, help="Podaj mierzoną wielkość(np: PM2.5, PM10, NO)", choices=["PM10", "PM2.5", "NO", "NO2", "NOX", "O3", "SO2", "CO", "C6H6"])
    parser.add_argument("--czestotliwosc", required=True, type=str, help="Podaj częstotliwość(1g/24g)")
    parser.add_argument("--przedzial_start", required=True, type=validate_date, help="Podaj początek przedziału czasowego(format: rrr-mm-dd)")
    parser.add_argument("--przedzial_koniec", required=True, type=validate_date, help="Podaj koniec przedziału czasowego(format: rrr-mm-dd)")

    subparser = parser.add_subparsers(dest="sub")
    parser_a = subparser.add_parser("losowo", help="Wypisuje nazwe i adres losowej stacji, która w zadanym przedziale czasowym mierzy podaną wielkość")
    parser_b = subparser.add_parser("srednia_odchylenie", help="Oblicza średnią i odchylenie standardowe danej wielkości w zadanym przedziale czasowym dla podanej stacji")
    parser_b.add_argument("--stacja", required=True, type=str, help="Podaj kod stacji")

    return parser.parse_args()

def validate_date(date):
    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("Nieprawidłowy format daty, date podaj w formacie: rrrr-mm-dd")

if __name__ == "__main__":
    args = parse()

    pomiary_path = r"C:\Users\kubap\PycharmProjects\PythonProject8\Lab5\measurements"
    stacje_path = r"C:\Users\kubap\PycharmProjects\PythonProject8\Lab5\stacje.csv"

    try:
        files = group_measurement_files_by_key(pomiary_path)
    except Exception as e:
        logger.error(f"Nie można wczytać katalogu z pomiarami: {e}")
        sys.exit(1)

    try:
        logger.info(f"Otwieranie pliku: {stacje_path}")
        stacje = parse_stacje(stacje_path)
        logger.info(f"Zamknięcie pliku: {stacje_path}")
    except Exception as e:
        logger.error(f"Plik nie istnieje: {stacje_path}")
        sys.exit(1)

    if args.sub == "losowo":
        res_kody = set()

        for year in range(args.przedzial_start.year, args.przedzial_koniec.year + 1):
            file = files.get((str(year), args.wielkosc, args.czestotliwosc))

            if file:
                logger.info(f"Otwieranie pliku: {file}")
                with open(file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f, delimiter=",")
                    rows = []
                    for row in reader:
                        bytes_count = sum(len(cell.encode("utf-8")) for cell in row)
                        logger.debug(f"Przeczytano wiersz: {bytes_count} bajtów")
                        rows.append(row)
                logger.info(f"Zamknięcie pliku: {file}")
                if len(rows) > 1:
                    kody = rows[1][1:]
                    for kod in kody:
                        if kod.strip():
                            res_kody.add(kod.strip())
            else:
                logger.warning(f"Brak pliku pomiarów")

        if not res_kody:
            logger.warning("Brak stacji")
        else:
            rand_kod = random.choice(list(res_kody))
            found_stacja = None
            for stacja in stacje:
                if stacja.get("kod") == rand_kod:
                    found_stacja = stacja
                    break

            if found_stacja:
                print(f"Wylosowana stacja:\n Nazwa: {found_stacja.get('nazwa')}\nAdres: {found_stacja.get('adres')}")
            else:
                logger.warning(f"Brak danych w stacje.csv")

    elif args.sub == "srednia_odchylenie":
        wartosci = []

        for year in range(args.przedzial_start.year, args.przedzial_koniec.year + 1):
            file = files.get((str(year), args.wielkosc, args.czestotliwosc))

            if not file:
                logger.warning(f"Brak pliku pomiarów")
                continue
            else:
                logger.info(f"Otwieranie pliku: {file}")
                with open(file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f, delimiter=",")
                    rows = []
                    for row in reader:
                        bytes_count = sum(len(cell.encode("utf-8")) for cell in row)
                        logger.debug(f"Przeczytano wiersz: {bytes_count} bajtów")
                        rows.append(row)
                logger.info(f"Zamknięcie pliku: {file}")
                kody_stacji = rows[1]

                try:
                    index_kolumny = kody_stacji.index(args.stacja)
                except ValueError:
                    logger.warning(f"Stacja nie występuje w pliku dla podanych argumentów")
                    continue


                pomiary = rows[6:]

                for wiersz in pomiary:
                    if not wiersz or not wiersz[0]:
                        continue

                    data = wiersz[0].split(" ")[0]
                    # print(data)

                    try:
                        data_pomiaru = datetime.datetime.strptime(data, "%m/%d/%y")

                        if args.przedzial_start <= data_pomiaru <= args.przedzial_koniec:
                            wartosc_str = wiersz[index_kolumny]

                            if wartosc_str.strip():
                                wartosc_float = float(wartosc_str.replace(",", "."))
                                wartosci.append(wartosc_float)

                    except ValueError:
                        continue
        if wartosci:
            srednia = statistics.mean(wartosci)
            odch = statistics.stdev(wartosci)

            print(f"Stacja {args.stacja}\nśrednia: {srednia:.2f}\nodcyhlenie: {odch:.2f}")
        else:
            logger.warning(f"Brak danych z pomiarów")
