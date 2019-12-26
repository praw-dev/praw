"""PRAW Test Suite."""
from abc import ABC, abstractmethod

class PrawTest(ABC):
    """A class representing the root of all test cases"""
    def __init__(self):
        self._testcases = []
        for attr in dir(self):
            if attr[0:4] == "test":
                self._testcases.append(getattr(self, attr))

    def __repr__(self, name = "Test Case"):
        return "PRAW {name} [{test_number} test cases]".format(
            name=self.__class__.__name__,
            test_number=len(self._testcases)
        )

    def __str__(self):
        return str(self._testcases)

    def __call__(self):
        return self.run_all_testcases()

    def __iter__(self):
        return self

    def __next__(self):
        for item in self._testcases:
            yield item

    def run_all_testcases(self):
        for item in dir(self):
            if item[0:4] == "test":
                case = getattr(self, item)
                case()

    @abstractmethod
    def setup(self):
        raise NotImplementedError("Make sure to run setup before starting tests.")