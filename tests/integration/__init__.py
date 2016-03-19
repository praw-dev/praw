"""PRAW Integration test suite."""
import pytest
from betamax import Betamax
from praw import Reddit


class IntegrationTest(object):
    """Base class for PRAW integration tests."""

    def setup(self):
        """Setup runs before all test cases."""
        self.reddit = Reddit(client_id=pytest.placeholders.client_id,
                             client_secret=pytest.placeholders.client_secret,
                             password=pytest.placeholders.password,
                             user_agent=pytest.placeholders.user_agent,
                             username=pytest.placeholders.username)

        http = self.reddit._core._requestor._http
        self.recorder = Betamax(http)

        # Disable response compression in order to see the response bodies in
        # the betamax cassettes.
        http.headers['Accept-Encoding'] = 'identity'

        # Require tests to explicitly disable read_only mode.
        self.reddit.read_only = True
