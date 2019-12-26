"""PRAW Test Suite."""
from abc import ABC, abstractmethod


class PrawTest(ABC):
    """A class representing the root of all test cases"""

    _testcases = []
    _ran_testcase_collection = False

    def _make_testcases(self):
        self._testcases = []
        self._ran_testcase_collection = False
        for attr in dir(self):
            if attr[0:4] == "test":
                self._testcases.append(getattr(self, attr))
        self._ran_testcase_collection = True

    def _check_for_testcases(self):
        if not self._ran_testcase_collection:
            self._make_testcases()

    def __repr__(self, name="Test Case"):
        self._check_for_testcases()
        return "PRAW {name} [{test_number} test cases]".format(
            name=name, test_number=len(self._testcases)
        )

    def __str__(self):
        self._check_for_testcases()
        return str(self._testcases)

    def __call__(self):
        return self.run_all_testcases()

    def __iter__(self):
        return self

    def __next__(self):
        self._check_for_testcases()
        for item in self._testcases:
            yield item

    def run_all_testcases(self):
        self._check_for_testcases()
        [testcase() for testcase in self._testcases]

    @abstractmethod
    def setup(self):
        raise NotImplementedError(
            "Make sure to run setup before starting tests."
        )
