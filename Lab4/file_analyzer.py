import json
import sys

def analyze():
    try:

        path = sys.stdin.readline().strip()
        file = open(path, "r", encoding="utf-8")
        content = file.read()
        words = content.split()

        charCount = len(content)
        wordCount = len(words)
        if content:
            nLineCount = content.count("\n") + 1
        else:
            nLineCount = 0
        mostFreqLetter = ""
        mostFreqWord = ""

        letterDict = {}
        for char in content:
            if char in letterDict:
                letterDict[char] += 1
            else:
                letterDict[char] = 1
        if letterDict:
            mostFreqLetter = max(letterDict, key=letterDict.get)

        wordDict = {}
        for word in words:
            if word in wordDict:
                wordDict[word] += 1
            else:
                wordDict[word] = 1
        if wordDict:
            mostFreqWord = max(wordDict, key=wordDict.get)

        result = {"path" : path, "letter_count" : charCount, "word_count" : wordCount, "line_count" : nLineCount, "most_freq_letter" : mostFreqLetter, "most_freq_word" : mostFreqWord, "letter_dict" : letterDict, "word_dict" : wordDict}
        jsonResult = json.dumps(result, ensure_ascii=False)

        print(jsonResult)

        file.close()
    except FileNotFoundError:
        print("Nie znaleziono pliku o podanej nazwie")
if __name__ == "__main__":
    analyze()