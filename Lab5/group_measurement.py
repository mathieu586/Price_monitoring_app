import os
import re
from pathlib import Path


def group_measurement_files_by_key(path):
    if not isinstance(path, Path):
        path = Path(path)

    pattern = r"^(\d{4})_(.+?)_([^_]+)\.csv$"
    result_dict = {}

    if not path.is_dir():
        print(f"Błąd, podana ścieżka nie prowadzi do folderu")
        return {}

    for file in path.iterdir():
        if file.is_file():
            result = re.match(pattern, file.name)
            if result:
                rok, wielkosc, czestotliwosc = result.groups()
                key = (rok, wielkosc, czestotliwosc)

                result_dict[key] = file


    return result_dict

if __name__ == "__main__":
    test1 = group_measurement_files_by_key(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\measurements")
    test2 = group_measurement_files_by_key(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\Empty_catalog")
    test3 = group_measurement_files_by_key(r"C:\Users\admin\PycharmProjects\PythonProject\Lab5\empty")

    print(len(test1))
    print(len(test2))
    print(len(test3))
