"""PRAW Integration test suite."""

from betamax import Betamax
from praw import Reddit
import pytest
import requests


class IntegrationTest:
    """Base class for PRAW integration tests."""

    def setup(self):
        """Setup runs before all test cases."""
        self._overrode_reddit_setup = True
        self.setup_reddit()
        self.setup_betamax()

    def setup_betamax(self):
        """Configure betamax instance based off of the reddit instance."""
        http = self.reddit._core._requestor._http
        self.recorder = Betamax(http)

        # Disable response compression in order to see the response bodies in
        # the betamax cassettes.
        http.headers["Accept-Encoding"] = "identity"

        # Require tests to explicitly disable read_only mode.
        self.reddit.read_only = True

        pytest.set_up_record = self.set_up_record  # used in conftest.py

    def setup_reddit(self):
        self._overrode_reddit_setup = False

        self._session = requests.Session()

        self.reddit = Reddit(
            requestor_kwargs={"session": self._session},
            client_id=pytest.placeholders.client_id,
            client_secret=pytest.placeholders.client_secret,
            password=pytest.placeholders.password,
            user_agent=pytest.placeholders.user_agent,
            username=pytest.placeholders.username,
        )

    def set_up_record(self):
        if not self._overrode_reddit_setup:
            if (
                pytest.placeholders.refresh_token
                != "placeholder_refresh_token"
            ):
                self.reddit = Reddit(
                    requestor_kwargs={"session": self._session},
                    client_id=pytest.placeholders.client_id,
                    client_secret=pytest.placeholders.client_secret,
                    user_agent=pytest.placeholders.user_agent,
                    refresh_token=pytest.placeholders.refresh_token,
                )
