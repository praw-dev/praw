"""Test praw.models.auth."""
from prawcore import InvalidToken
from praw import Reddit
from six import string_types
import pytest

from .. import IntegrationTest


class TestAuthWeb(IntegrationTest):
    def setup_reddit(self):
        self.reddit = Reddit(client_id=pytest.placeholders.client_id,
                             client_secret=pytest.placeholders.client_secret,
                             redirect_uri=pytest.placeholders.redirect_uri,
                             user_agent=pytest.placeholders.user_agent)

    def test_authorize(self):
        with self.recorder.use_cassette('TestAuthWeb.test_authorize'):
            token = self.reddit.auth.authorize(pytest.placeholders.auth_code)
            assert isinstance(token, string_types)


class TestAuthImplicit(IntegrationTest):
    def setup_reddit(self):
        self.reddit = Reddit(client_id=pytest.placeholders.client_id,
                             client_secret=None,
                             user_agent=pytest.placeholders.user_agent)

    def test_implicit__with_invalid_token(self):
        self.reddit.auth.implicit('invalid_token', 10, 'read')
        with self.recorder.use_cassette(
                'TestAuthImplicit.test_implicit__with_invalid_token'):
            with pytest.raises(InvalidToken):
                self.reddit.user.me()
