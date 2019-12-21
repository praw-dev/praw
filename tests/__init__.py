"""PRAW Test Suite."""


class PrawTest:
    def __repr__(self, test_type="Test Class"):
        testcases = [
            None for item in dir(self) if item[0:4].lower() == "test"
        ].count(None)
        return "PRAW %s <%s> [%s test cases]" % (
            test_type,
            self.__class__.__module__,
            testcases,
        )
