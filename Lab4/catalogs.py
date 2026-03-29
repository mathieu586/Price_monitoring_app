import os
import sys


def getCatalogs():
    value = os.environ["PATH"]
    catalogs = (value.split(os.pathsep))

    return catalogs

def printCatalogs():
    catalogs = getCatalogs()

    for catalog in catalogs:
        print(catalog)

def printExecs():
    catalogs = getCatalogs()

    for catalog in catalogs:
        print(catalog, end=":\n")
        if os.path.isdir(catalog):
            try:
                files = os.listdir(catalog)
                for file in files:
                    if os.name == "nt":
                        if file.lower().endswith((".exe", ".bat", ".cmd")):
                            print(file)
                    else:
                        path = os.path.join(catalog, file)
                        if os.access(path, os.X_OK):
                            print(file)
            except PermissionError as e:
                print(e)

        print(100 * "-")


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Podaj argument: 'catalog' lub 'file'")
    else:
        if sys.argv[1] == "catalog":
            printCatalogs()
        else:
            printExecs()
