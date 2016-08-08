"""Test praw.models.auth."""
from prawcore import InvalidToken
import pytest

from .. import UntrustedIntegrationTest


class TestAuthImplicit(UntrustedIntegrationTest):
    def test_implicit__with_invalid_token(self):
        self.reddit.auth.implicit('invalid_token', 10, 'read')
        with self.recorder.use_cassette(
                'TestAuthImplicit.test_implicit__with_invalid_token'):
            with pytest.raises(InvalidToken):
                self.reddit.user.me()
