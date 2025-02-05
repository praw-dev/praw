"""Test praw.models.auth."""

import pytest
from prawcore import InvalidToken

from praw import Reddit

from .. import IntegrationTest


class TestAuthImplicit(IntegrationTest):
    @pytest.fixture
    def reddit(self, recorder):
        return Reddit(
            client_id=pytest.placeholders.client_id,
            client_secret=None,
            requestor_kwargs={"session": recorder.session},
            user_agent=pytest.placeholders.user_agent,
        )

    def test_implicit__with_invalid_token(self, reddit):
        reddit.auth.implicit(access_token="invalid_token", expires_in=10, scope="read")
        with pytest.raises(InvalidToken):
            reddit.user.me()

    def test_scopes__read_only(self, reddit):
        assert reddit.read_only is True
        assert reddit.auth.scopes() == {"*"}


class TestAuthScript(IntegrationTest):
    def test_scopes(self, reddit):
        assert reddit.read_only is True
        assert reddit.auth.scopes() == {"*"}


class TestAuthWeb(IntegrationTest):
    @pytest.fixture
    def reddit(self, recorder):
        return Reddit(
            client_id=pytest.placeholders.client_id,
            client_secret=pytest.placeholders.client_secret,
            redirect_uri=pytest.placeholders.redirect_uri,
            requestor_kwargs={"session": recorder.session},
            user_agent=pytest.placeholders.user_agent,
            username=None,
        )

    def test_authorize(self, reddit):
        token = reddit.auth.authorize(pytest.placeholders.auth_code)
        assert isinstance(token, str)
        assert reddit.read_only is False
        assert reddit.auth.scopes() == {"submit"}

    def test_scopes__read_only(self, reddit):
        assert reddit.read_only is True
        assert reddit.auth.scopes() == {"*"}
