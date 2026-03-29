import os
import sys

def printVariables():
    variables = sorted(os.environ)

    for var in variables:
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg.upper() in var.upper():
                    value = os.environ[var]
                    print(f"{var}: {value}")
                    break
        else:
            value = os.environ[var]
            print(f"{var}: {value}")


if __name__ == "__main__":
    printVariables()