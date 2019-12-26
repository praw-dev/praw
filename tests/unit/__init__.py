"""PRAW Unit test suite."""
from praw import Reddit

from .. import PrawTest


class UnitTest(PrawTest):
    """Base class for PRAW unit tests."""

    def __repr__(self, name="Unit Test"):
        return super().__repr__(name)

    def setup(self):
        """Setup runs before all test cases."""
        self.reddit = Reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy"
        )
        # Unit tests should never issue requests
        self.reddit._core._requestor._http = None
