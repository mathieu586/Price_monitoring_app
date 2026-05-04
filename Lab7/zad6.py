import logging
import time
import sys
from functools import wraps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout  )

def log(level=logging.DEBUG):
    def decorator(target):
        if isinstance(target, type):
            original = target.__init__
            @wraps(original)
            def new_init(self, *args, **kwargs):
                logging.log(level, f"Instancjonowanie klasy '{target.__name__}'"
                                   f"args = {args}, kwargs = {kwargs}")
                original(self, *args, **kwargs)
            target.__init__ = new_init
            return target
        @wraps(target)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            calltime = time.strftime("%H:%M:%S", time.localtime())
            result = target(*args, **kwargs)
            duration = time.perf_counter() - start
            logging.log(level, f"Funkcja '{target.__name__}' wywołana {calltime}, "
                               f"czas trwania: {duration:.6f},"
                               f" args = {args}, kwargs = {kwargs}"
                               f" wynik = {result}")
            return result
        return wrapper
    return decorator

@log(level=logging.DEBUG)
def add(a, b):
    return a + b

@log(level=logging.DEBUG)
class Square:
    def __init__(self, x):
        self.x = x

if __name__ == '__main__':
    print(add(1, 2))
    print(add(1, b=2))
    kwadrat = Square(3)
