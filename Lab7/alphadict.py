def make_alpha_dict(s):
    words = s.lower().split()
    chars = sorted(set(ch for ch in s.lower() if ch.isalpha()))
    alpha_dict = {ch: [word for word in words if ch in word] for ch in chars}
    return alpha_dict

if __name__ == "__main__":
    print(make_alpha_dict("on i ona"))
    print(make_alpha_dict("a AAA ad dasda"))
    print(make_alpha_dict("12a3 xfd"))
    print(make_alpha_dict(""))
