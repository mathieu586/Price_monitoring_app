# Price Monitor

Aplikacja desktopowa do monitorowania cen produktów w sklepach internetowych. Umożliwia śledzenie historii cen, ustawianie alertów cenowych oraz automatyczne sprawdzanie cen w zadanych odstępach czasu.

---

## Spis treści

- [Wymagania i zależności](#wymagania-i-zależności)
- [Uruchomienie](#uruchomienie)
- [Budowanie pliku wykonywalnego (.exe)](#budowanie-pliku-wykonywalnego-exe)
- [Struktura projektu](#struktura-projektu)
- [Instrukcja dla użytkownika](#instrukcja-dla-użytkownika)

---

## Wymagania i zależności

**Python:** 3.11+

Wymagane biblioteki:

| Biblioteka | Zastosowanie |
|---|---|
| `customtkinter` | Graficzny interfejs użytkownika |
| `CTkMessagebox` | Okna dialogowe i komunikaty |
| `requests` | Pobieranie stron internetowych |
| `beautifulsoup4` | Parsowanie HTML i ekstrakcja cen |
| `pyinstaller` | Budowanie pliku .exe (opcjonalnie) |

Instalacja wszystkich zależności:

```bash
pip install -r requirements
```

---

## Uruchomienie

**Krok 1 - Utwórz środowisko wirtualne:**

```bash
cd C:\Users\<TwojaNazwa>\Python\Jezyki_skryptowe_laby
python -m venv .venv
```

**Krok 2 - Zainstaluj zależności:**

```bash
.venv\Scripts\pip install -r .\Projekt\requirements.txt
```

**Krok 3 - Uruchom aplikację:**

```bash
cd Projekt
..\.venv\Scripts\python src/main.py
```

Lub bezpośrednio z katalogu `Projekt`:

```bash
python src/main.py
```

> Środowisko wirtualne `.venv` nie jest częścią repozytorium i trzeba je stworzyć lokalnie na każdej maszynie.

---

## Budowanie pliku wykonywalnego (.exe)

Aby zbudować samodzielny plik `.exe` (nie wymaga zainstalowanego Pythona):

1. Upewnij się, że masz zainstalowany `pyinstaller` w środowisku wirtualnym:
   ```bash
   ..\.venv\Scripts\pip install pyinstaller
   ```

2. Z katalogu `Projekt` uruchom skrypt budujący:
   ```bash
   build.bat
   ```

Gotowy plik wykonywalny pojawi się w folderze `dist/PriceMonitor/PriceMonitor.exe`.

---

## Struktura projektu

```
Projekt/
├── build.bat               # Skrypt budujący plik .exe
└── src/
    ├── main.py             # Punkt startowy aplikacji
    ├── gui.py              # Główne okno aplikacji i interfejs użytkownika
    ├── models.py           # Modele danych: Product, PriceRecord, ProductStats
    ├── scraper.py          # Pobieranie i ekstrakcja cen ze stron www
    ├── monitor.py          # Logika monitorowania i wyzwalania alertów
    ├── repository.py       # Zapis i odczyt produktów
    ├── stores.py           # Konfiguracja sklepów i selektorów CSS
    ├── product_data.json   # Baza danych produktów (generowana automatycznie)
    └── stores.json         # Własne sklepy użytkownika (generowany automatycznie)
```

### Opis modułów

**`main.py`** - punkt wejścia aplikacji.

**`gui.py`** - Zawiera główne okno (`Main_window`) oraz wszystkie okna pomocnicze (dodawanie produktu, edycja, historia cen, zarządzanie sklepami).

**`models.py`** - definicje klas danych: `Product` (produkt), `PriceRecord` (pojedynczy wpis cenowy), `ProductStats` (statystyki produktu).

**`scraper.py`** - pobiera stronę produktu przez HTTP i wyodrębnia cenę na podstawie selektora CSS. Obsługuje różne waluty (PLN, EUR, USD, GBP) i statusy błędów.

**`monitor.py`** - sprawdza cenę produktu przez scraper, zapisuje wynik do repozytorium i wywołuje alert, jeśli cena spadła poniżej progu.

**`repository.py`** - przechowywanie danych: `JsonRepository` (zapis do pliku `product_data.json`) i `MemoryRepository` (tylko w pamięci, do testów).

**`stores.py`** - rejestr sklepów z selektorami CSS dla przykładowych serwisów . Obsługuje też sklepy własne zapisywane w `stores.json`.

---

## Instrukcja dla użytkownika

### Widok główny

Po uruchomieniu aplikacji wyświetla się główne okno podzielone na dwie sekcje:

- **lewa część** - tabela z listą monitorowanych produktów
- **prawa część** - panel powiadomień i alertów


---

### Dodawanie produktu

1. Kliknij przycisk **Dodaj**.
2. Wypełnij formularz:
   - **Nazwa** - dowolna nazwa produktu
   - **Link URL** - pełny adres strony produktu
   - **Próg alarmowy** - cena, poniżej której chcesz dostać powiadomienie (opcjonalne)
3. Kliknij **Dodaj Produkt**.

> Aplikacja automatycznie rozpoznaje sklep na podstawie domeny URL i dobiera odpowiedni selektor ceny. Jeśli sklep nie jest rozpoznany, pojawi się komunikat o błędzie - dodaj go ręcznie w oknie **Sklepy**.

**Obsługiwane sklepy (wbudowane):** Ceneo, Morele, Books to Scrape, Oxylabs Sandbox.

---

### Edytowanie produktu

1. Zaznacz produkt w tabeli.
2. Kliknij przycisk **Edytuj**.
3. Zmień dane produktu.
4. Kliknij **Zapisz**.

---

### Usuwanie produktu

1. Zaznacz produkt w tabeli.
2. Kliknij przycisk **Usuń**.

Produkt zostaje usunięty razem z całą historią cen.

---

### Sprawdzanie ceny

**Ręcznie - jeden produkt:**
1. Zaznacz produkt w tabeli.
2. Kliknij **Sprawdź cenę**.
3. Cena zostanie pobrana i zaktualizowana w tabeli.

**Ręcznie - wszystkie produkty:**
Kliknij **Sprawdź wszystkie** - aplikacja pobierze ceny wszystkich produktów po kolei.

**Automatycznie - pętla monitorowania:**
1. W polu **Interwał [s]** wpisz co ile sekund mają być sprawdzane ceny (np. `3600` = co godzinę).
2. Kliknij **Start** - przycisk zmieni się na **Stop** i rozpocznie się monitorowanie.
3. Kliknij **Stop**, aby zatrzymać automatyczne sprawdzanie.

---

### Historia cen

1. Zaznacz produkt w tabeli.
2. Kliknij **Historia**.
3. Otwiera się okno z pełną historią: data, cena, waluta, dostępność i status każdego sprawdzenia (od najnowszych).

---

### Zarządzanie sklepami

Kliknij **Sklepy**, aby otworzyć okno zarządzania sklepami.

Widoczna jest lista wszystkich sklepów (wbudowanych i własnych). Sklepy wbudowane wyświetlone są jako `wbudowany` w kolumnie `Typ` i są one tylko do odczytu.

**Dodawanie własnego sklepu:**
1. Kliknij **Dodaj** w oknie sklepów.
2. Wypełnij pola:
   - **Nazwa** - nazwa sklepu
   - **Domena** - fragment domeny URL (np. `ceneo.pl`)
   - **Waluta** - kod waluty (np. `PLN`, `EUR`)
   - **Selektor CSS** - selektor HTML wskazujący element z ceną na stronie (np. `.price-value`); zostaw puste, żeby użyć selektorów domyślnych. Selektory domyślne nie gwarantują poprawnego działania scrapera
   - **Uwagi** - opcjonalne notatki
3. Kliknij **Zapisz**.

---

### Eksport i import danych

**Eksport:** Kliknij **Eksport** - zostanie wyświetlone okno zapisu pliku. Wybierz lokalizację i zapisz dane produktów w formacie JSON.

**Import:** Kliknij **Import** - wybierz wcześniej wyeksportowany plik JSON. Produkty zostaną wczytane do aplikacji.

Funkcja ta pozwala przenosić dane między komputerami lub tworzyć kopie zapasowe.

---

### Panel powiadomień

Prawa część okna wyświetla logi zdarzeń w czasie rzeczywistym:

- `[SYSTEM]` – operacje systemowe (dodanie/usunięcie produktu)
- `[ALERT]` – cena produktu spadła poniżej ustawionego progu alarmowego
- Błędy i statusy pobierania cen

Kliknij **Wyczyść**, aby usunąć wszystkie powiadomienia z panelu.

---

### Sortowanie listy produktów

Nad tabelą produktów znajduje się wiersz filtrów. Kliknij jeden z przycisków, aby posortować listę według:

- **Data dodania** - od najnowszych
- **Nazwa** - alfabetycznie
- **Cena** - od najniższej
- **Sklep** - alfabetycznie według nazwy sklepu
- **Termin zmiany** - od ostatnio zaktualizowanych

---

### Przechowywanie danych

Dane są przechowywane lokalnie w katalogu, z którego uruchomiono aplikację:

- `product_data.json` - historia cen i dane wszystkich produktów
- `stores.json` - własne sklepy dodane przez użytkownika

Pliki te są aktualizowane automatycznie przy każdej zmianie.
