from functools import reduce

def group_anagrams(ls):
    return reduce(lambda acc, w: {**acc, "".join(sorted(w)): acc.get(''.join(sorted(w)),[]) + [w]}, ls, {})

if __name__ == '__main__':
    print(group_anagrams(["kot", "tok", "pies", "kep", "pek"]))
    print(group_anagrams(["kajak", "kajak", "ajak", "kot"]))
    print(group_anagrams([" ", "abc1"]))

