"""Test praw.models.auth."""
from prawcore import InvalidToken
from praw import Reddit
from six import string_types
import pytest

from .. import IntegrationTest


class TestAuthScript(IntegrationTest):
    def test_scopes(self):
        with self.recorder.use_cassette('TestAuthScript.test_scopes'):
            assert self.reddit.read_only is True
            assert self.reddit.auth.scopes() == {'*'}


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
            assert self.reddit.read_only is False
            assert self.reddit.auth.scopes() == {'submit'}

    def test_scopes__read_only(self):
        with self.recorder.use_cassette('TestAuthWeb.test_scopes__read_only'):
            assert self.reddit.read_only is True
            assert self.reddit.auth.scopes() == {'*'}


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

    def test_scopes__read_only(self):
        with self.recorder.use_cassette(
                'TestAuthImplicit.test_scopes__read_only'):
            assert self.reddit.read_only is True
            assert self.reddit.auth.scopes() == {'*'}
