import sys
import csv
from pathlib import Path
from datetime import datetime
from peewee import *
from Models import Station, Rental, init_db


COLUMN_ALIASES = {
    "uid wynajmu": "uid",
    "numer roweru": "bike",
    "data wynajmu": "start",
    "data zwrotu": "end",
    "stacja wynajmu": "rental_station",
    "stacja zwrotu": "return_station",
    "czas trwania": "duration",
}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BATCH_SIZE = 1000

def parse_date(date):
    date = date.strip()
    if not date:
        return None
    try:
        return datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        return None

def normalize_headers(raw):
    return COLUMN_ALIASES.get(raw.strip().lower(), raw.strip().lower())

def get_or_create_station(station_cache, station_name):
    name = station_name.strip()
    if name in station_cache:
        return station_cache[name]
    station, _ = Station.get_or_create(station_name = name)
    station_cache[name] = station
    return station

def load_csv(csv_path, db_name):
    init_db(db_name)

    path = Path(csv_path)
    if not path.exists():
        print("Podano nieprawidłowy plik .csv")
        sys.exit(1)

    station_cache = {}
    inserted = 0
    skipped = 0
    errors = 0

    with path.open(encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        _ = reader.fieldnames
        reader.fieldnames = [normalize_headers(h) for h in reader.fieldnames]
        print(reader.fieldnames)
        batch_rentals = []
        def flush(batch):
            nonlocal inserted, skipped
            with Station._meta.database.atomic():
                for r in batch:
                    try:
                        Rental.insert(r).on_conflict_ignore().execute()
                        inserted += 1
                    except IntegrityError:
                        skipped += 1

        for i, row in enumerate(reader, start=1):
            try:
                uid = row.get("uid", "").strip()
                if not uid:
                    skipped += 1
                    continue

                bike_raw = row.get("bike", "0").strip()
                bike_number = int(bike_raw) if bike_raw.isdigit() else 0

                start_time = parse_date(row.get("start", ""))
                end_time = parse_date(row.get("end", ""))

                dur_raw = row.get("duration", "").strip()
                duration = int(float(dur_raw)) if dur_raw else None

                rental_station_name = row.get("rental_station", "").strip()
                return_station_name = row.get("return_station", "").strip()

                if not rental_station_name:
                    skipped += 1
                    continue

                rental_station = get_or_create_station(station_cache, rental_station_name)
                return_station = get_or_create_station(station_cache, return_station_name) if return_station_name else None

                batch_rentals.append({
                    "rental_id": uid,
                    "bike_number": bike_number,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "rental_station_id": rental_station.station_id,
                    "return_station_id": return_station.station_id if return_station else None,
                })

                if len(batch_rentals) >= BATCH_SIZE:
                    flush(batch_rentals)
                    batch_rentals.clear()

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"Ostrzeżenie, wiersz {i}: {e}")

        if batch_rentals:
            flush(batch_rentals)

    print(f"\n Plik: {csv_path}")
    print(f"  Wstawiono:  {inserted}")
    print(f"  Pominięto:  {skipped}")
    print(f"  Błędy:      {errors}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python load_data.py plik nazwa_bazy")
        sys.exit(1)

    load_csv(sys.argv[1], sys.argv[2])