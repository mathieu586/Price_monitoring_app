import os
import sys
import time
import argparse

def read_last(all_lines, n):
    lines = list(all_lines)
    if n == 0:
        return []
    return lines[-n:] if n < len(lines) else lines

def tail_from_file(path, n, follow):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = read_last(f, n)
            sys.stdout.writelines(lines)
        if follow:
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        sys.stdout.write(line.decode("utf-8", errors="replace"))
                        sys.stdout.flush()
                    else:
                        time.sleep(0.1)
    except FileNotFoundError:
        print("Brak pliku o podanej nazwie")
        sys.exit(1)
    except PermissionError:
        print("Brak uprawnień")
        sys.exit(1)

def tail_write(n):
    lines = read_last(sys.stdin, n)
    sys.stdout.writelines(lines)

def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument("--lines", type=int, default=10, metavar="N", help="Liczba linii do wyświetlenia")
    parser.add_argument("--follow", action="store_true", help="śledź nowe linie")
    parser.add_argument("file", nargs="?", help="Ścieżka pliku")
    return parser.parse_args()

def main():
    args = parse()
    if args.lines < 0:
        print("Liczba linii nie może być ujemna")
        sys.exit(1)

    if args.file:
        tail_from_file(args.file, args.lines, args.follow)
    else:
        tail_write(args.lines)

if __name__ == "__main__":
    main()