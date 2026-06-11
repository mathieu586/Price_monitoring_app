import sys
from Models import init_db

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Użycie: python create_database.py nazwa_bazy")
        sys.exit(1)

    init_db(sys.argv[1])
    print(f"Utworzono bazę o nazwie {sys.argv[1]}.sqlite3")