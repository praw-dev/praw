"""PRAW Integration test suite."""
import inspect
import logging

import pytest
import requests
from betamax import Betamax

from praw import Reddit


class IntegrationTest:
    """Base class for PRAW integration tests."""

    logger = logging.getLogger(__name__)

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
            if pytest.placeholders.refresh_token != "placeholder_refresh_token":
                self.reddit = Reddit(
                    requestor_kwargs={"session": self._session},
                    client_id=pytest.placeholders.client_id,
                    client_secret=pytest.placeholders.client_secret,
                    user_agent=pytest.placeholders.user_agent,
                    refresh_token=pytest.placeholders.refresh_token,
                )

    def use_cassette(self, cassette_name=None, **kwargs):
        """Use a cassette. The cassette name is dynamically generated.

        :param cassette_name: (Deprecated) The name to use for the cassette. All names
            that are not equal to the dynamically generated name will be logged.
        :param kwargs: All keyword arguments for the main function
            (``Betamax.use_cassette``).
        """
        dynamic_name = self.get_cassette_name()
        if cassette_name:
            self.logger.debug(
                f"Static cassette name provided by {dynamic_name}. The following name "
                f"was provided: {cassette_name}"
            )
            if cassette_name != dynamic_name:
                self.logger.warning(
                    f"Dynamic cassette name for function {dynamic_name} does not match"
                    f" the provided cassette name: {cassette_name}"
                )
        return self.recorder.use_cassette(cassette_name or dynamic_name, **kwargs)

    def get_cassette_name(self) -> str:
        function_name = inspect.currentframe().f_back.f_back.f_code.co_name
        return f"{type(self).__name__}.{function_name}"
