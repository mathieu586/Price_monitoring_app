import random
import string


class PasswordGenerator:
    def __init__(self, length, count, charset = string.ascii_letters + string.digits):
        self.length = length
        self.charset = charset
        self.count = count
        self.generated_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.generated_count >= self.count:
            raise StopIteration("Osiągnięto limit generowania haseł")

        password = ""
        for i in range(self.length):
            rand_char = random.choice(self.charset)
            password += rand_char

        self.generated_count += 1

        return password



if __name__ == "__main__":
    password_gen_1 = PasswordGenerator(6, 3, charset="abcdefg1234")

    for i in range(3):
        print(next(password_gen_1))

    print()

    password_gen_2 = PasswordGenerator(10, 2)
    print(next(password_gen_2))

    password_gen_3 = PasswordGenerator(0, 1)
    print(next(password_gen_3))

    print()
    password_gen_4 = PasswordGenerator(5, 3, "a1")

    for i in range(4):
        try:
            print(next(password_gen_4))
        except StopIteration as e:
            print(f"Złapano wyjątek: {e}")