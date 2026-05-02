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


