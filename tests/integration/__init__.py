"""PRAW Integration test suite."""
import pytest
from betamax import Betamax
from praw import Reddit


class IntegrationTest:
    """Base class for PRAW integration tests."""

    def setup(self):
        """Setup runs before all test cases."""
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

    def setup_reddit(self):
        login_data = dict(
            client_id=pytest.placeholders.client_id,
            client_secret=pytest.placeholders.client_secret,
            refresh_token=pytest.placeholders.refresh_token,
            user_agent=pytest.placeholders.user_agent,
            username=pytest.placeholders.username,
        )
        if (
            login_data["username"] == "placeholder_username"
            and login_data["refresh_token"] != "placeholder_refresh_token"
        ):
            # Some refresh tokens do not require a username to be given
            login_data.pop("username")
        self.reddit = Reddit(**login_data)
