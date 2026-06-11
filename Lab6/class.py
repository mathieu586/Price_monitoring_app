from abc import ABC, abstractmethod
import statistics

class Klasa:
    def __init__(self, test):
        self.test = test

    def __str__(self):
        return "test"

    def __repr__(self):
        return "reprezentacja"

    def __eq__(self, other):
        return self.test == self.test

class Dziedziczaca(Klasa):
    def __init__(self, test):
        super.__init__(test)

class Abstrakcyjna(ABC):
    def __init__(self, test):
        self.test = test

    @abstractmethod
    def metoda_abs(self):
        pass

# @property pozwala wywolywac metode bez ()