import json
import sys
import os
import subprocess
from collections import Counter

def analyze():
    try:
        filesRead = 0
        charCount = 0
        wordCount = 0
        nLineCount = 0
        globalLetterDict = Counter()
        globalWordDict = Counter()
        mostFreqLetter = ""
        mostFreqWord = ""

        results = []
        catalogPath = sys.argv[1]
        if os.path.isdir(catalogPath):
            try:
                for file in os.listdir(catalogPath):
                    fullPath = os.path.join(catalogPath, file)

                    if os.path.isfile(fullPath):
                        content = subprocess.run([sys.executable, "file_analyzer.py"], input=fullPath, capture_output=True, text=True)

                        result = json.loads(content.stdout)
                        results.append(result)
                        filesRead += 1
                        charCount += result["letter_count"]
                        wordCount += result["word_count"]
                        nLineCount += result["line_count"]
                        globalLetterDict.update(result["letter_dict"])
                        globalWordDict.update(result["word_dict"])

                if globalLetterDict:
                    mostFreqLetter = max(globalLetterDict, key=globalLetterDict.get)
                if globalWordDict:
                    mostFreqWord = max(globalWordDict, key=globalWordDict.get)

                print(f"liczba przeczytanych plików: {filesRead}, liczba znaków: {charCount}, liczba słów: {wordCount}, liczba wierszy: {nLineCount}, najczęstszy znak: {mostFreqLetter}, najczęstszy wyraz: {mostFreqWord}")
            except PermissionError:
                print("Błąd uprawnień")
    except IndexError:
        print("Nie podano ścieżki")

if __name__ == "__main__":
    analyze()