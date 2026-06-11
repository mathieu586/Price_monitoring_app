import sys
import sqlite3

def create_database(db_name):
    path = db_name if db_name.endswith(".sqlite3") else db_name + ".sqlite3"

    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Stations (
        station_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name VARCHAR(255) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Rentals (
        rental_id INTEGER PRIMARY KEY,
        bike_number INTEGER NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME,
        duration INTEGER,

        rental_station_id INTEGER NOT NULL,
        return_station_id INTEGER,

        FOREIGN KEY (rental_station_id)
            REFERENCES Stations(station_id),

        FOREIGN KEY (return_station_id)
            REFERENCES Stations(station_id)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python create_database_sql.py nazwa_bazy")
        sys.exit(1)

    create_database(sys.argv[1])
    print(f"Utworzono bazę {sys.argv[1]}.sqlite3")