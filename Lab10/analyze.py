from peewee import fn
import sys
from Models import db, init_db, Station, Rental

def run(db_path):
    try:
        init_db(db_path)
    except Exception as e:
        print(f"Błąd połączenia z bazą danych: {e}")
        return

    stations = list(Station.select().order_by(Station.station_name))

    if not stations:
        print("Błędna ścieżka lub brak stacji w podanej ścieżce")
        return

    print("===== STACJE DO WYBORU: =====")
    for station in stations:
        print(f"[{station.station_id}]: {station.station_name}")

    chosen_id = input("\nPodaj id wybranej stacji: ")

    str_ids = [str(station.station_id) for station in stations]

    while chosen_id not in str_ids:
        print(f"Stacja o id: {chosen_id} nie istnieje!")
        chosen_id = input("\nPodaj id wybranej stacji: ")

    chosen_station = Station.get(Station.station_id == int(chosen_id))

    avg_start_dur = Rental.select(fn.AVG(Rental.duration)).where(Rental.rental_station == chosen_station).scalar()
    print(f"Średni czas trwania przejazdu rozpoczynanego na stacji {chosen_station.station_name} = {avg_start_dur:.2f} min")\
        if avg_start_dur is not None else print(f"Brak przejazdów rozpoczynających się na stacji: {chosen_station.station_name}")

    avg_end_dur = Rental.select(fn.AVG(Rental.duration)).where(Rental.return_station == chosen_station).scalar()
    print(f"Średni czas trwania przejazdu kończonego na stacji {chosen_station.station_name} = {avg_end_dur:.2f} min")\
        if avg_end_dur is not None else print(f"Brak przejazdów kończących się na stacji: {chosen_station.station_name}")

    bike_count = (Rental.select(fn.COUNT(Rental.bike_number.distinct())).
                  where((Rental.return_station == chosen_station) | (Rental.rental_station == chosen_station)).scalar())
    print(f"Liczba różnych rowerów parkowanych na stacji {chosen_station.station_name} = {bike_count}")

    most_freq = (Station.select(Station.station_name, fn.COUNT(Rental.rental_id).alias('ilosc_przejazdow'))
                 .join(Rental, on=(Station.station_id == Rental.return_station)).where(Rental.rental_station == chosen_station)
                 .group_by(Station.station_id).order_by(fn.COUNT(Rental.rental_id).desc()).limit(1).tuples().first())
    print(f"Najczęstsza stacja końcowa dla rowerów wypożyczanych na stacji {chosen_station.station_name} to {most_freq[0]}") if most_freq is not None else print(f"Nie znaleziono najczęstszej stacji końcowej dla rowerów wypożyczanych na stacji {chosen_station.station_name}, powód: brak stacji końcowych")

    db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python analyze.py ścieżka_bazy")
        sys.exit(1)

    run(sys.argv[1])