import logging
import os

logger = logging.getLogger(__name__)

def check_readable(path):
    if not path.exists():
        return False, "Plik nie istnieje"
    if not path.is_file():
        return False, "Nie wskazano pliku"
    try:
        with open(path, "rb") as f:
            pass  # Jeśli się udało otworzyć, plik jest czytelny
    except PermissionError:
        return False, "Brak uprawnień do pliku"
    except Exception as e:
        return False, f"Inny błąd odczytu: {e}"
    return True, ""

def check_writable(path):
    if path.exists():
        try:
            with open(path, "a") as f:
                pass
        except PermissionError:
            return False, "Brak uprawnień zapisu do pliku"
    else:
        try:
            test_file = path.parent / ".writable_test"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            return False, "Brak uprawnień zapisu do folderu"
        except Exception:
            return False, "Brak uprawnień zapisu do folderu"
    return True, ""