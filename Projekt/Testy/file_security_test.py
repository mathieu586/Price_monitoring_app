import sys
import subprocess
from src.file_security import check_readable, check_writable

class TestCheckReadable:

    def test_plik_istnieje(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text("{}", encoding="utf-8")
        ok, msg = check_readable(f)
        assert ok is True
        assert msg == ""

    def test_plik_nie_istnieje(self, tmp_path):
        f = tmp_path / "nieistniejacy.json"
        ok, msg = check_readable(f)
        assert ok is False
        assert msg != ""

    def test_katalog_zamiast_pliku(self, tmp_path):
        ok, msg = check_readable(tmp_path)
        assert ok is False
        assert msg != ""

    def test_brak_uprawnien_odczytu(self, tmp_path):
        f = tmp_path / "locked.json"
        f.write_text("{}", encoding="utf-8")

        if sys.platform == "win32":
            subprocess.run(["icacls", str(f), "/deny", "Wszyscy:(R)"], check=True, capture_output=True)
        else:
            f.chmod(0o000)
        try:
            ok, msg = check_readable(f)
            assert ok is False
            assert msg != ""
        finally:
            if sys.platform == "win32":
                subprocess.run(["icacls", str(f), "/remove:d", "Wszyscy"], check=True, capture_output=True)
            else:
                f.chmod(0o644)

class TestCheckWritable:
    def test_plik_istnieje(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text("{}", encoding="utf-8")
        ok, msg = check_writable(f)
        assert ok is True
        assert msg == ""

    def test_plik_nie_istnieje(self, tmp_path):
        f = tmp_path / "nowy.json"
        ok, msg = check_writable(f)
        assert ok is True
        assert msg == ""

    def test_brak_uprawnien_zapisu_plik(self, tmp_path):
        f = tmp_path / "locked_write.json"
        f.write_text("{}", encoding="utf-8")

        if sys.platform == "win32":
            subprocess.run(["icacls", str(f), "/deny", "Wszyscy:(W)"], check=True, capture_output=True)
        else:
            f.chmod(0o444)

        try:
            ok, msg = check_writable(f)
            assert ok is False
            assert msg != ""
        finally:
            if sys.platform == "win32":
                subprocess.run(["icacls", str(f), "/remove:d", "Wszyscy"], check=True, capture_output=True)
            else:
                f.chmod(0o644)

    def test_brak_uprawnien_zapisu_folder(self, tmp_path):
        protected_dir = tmp_path / "protected_folder"
        protected_dir.mkdir()

        target_file = protected_dir / "new_file.json"
        if sys.platform == "win32":
            subprocess.run(["icacls", str(protected_dir), "/deny", "Wszyscy:(W)"], check=True, capture_output=True)
        else:
            protected_dir.chmod(0o555)

        try:
            ok, msg = check_writable(target_file)
            assert ok is False
            assert msg != ""
        finally:
            if sys.platform == "win32":
                subprocess.run(["icacls", str(protected_dir), "/remove:d", "Wszyscy"], check=True, capture_output=True)
            else:
                protected_dir.chmod(0o755)