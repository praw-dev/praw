"""Test praw.models.auth."""
from prawcore import InvalidToken
from praw import Reddit
import pytest

from .. import IntegrationTest


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
