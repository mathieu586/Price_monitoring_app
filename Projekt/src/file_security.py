import logging
import os

logger = logging.getLogger(__name__)

def check_readable(path):
    if not path.exists():
        return False, "Plik nie istnieje"
    if not path.is_file():
        return False, "Nie wskazano pliku"
    if not os.access(path, os.R_OK):
        return False, "Brak uprawnień do pliku"
    return True, ""

def check_writable(path):
    if path.exists():
        if not os.access(path, os.W_OK):
            return False, "Brak uprawnień zapisu do pliku"
    else:
        if not os.access(path.parent, os.W_OK):
            return False, "Brak uprawnień zapisu do folderu"
    return True, ""