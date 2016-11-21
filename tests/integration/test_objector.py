"""Test praw.objector."""
from praw.exceptions import APIException
import pytest

from . import IntegrationTest


class TestObjector(IntegrationTest):
    def test_raise_api_exception(self):
        message = 'USER_REQUIRED: \'Please log in to do that.\''
        with self.recorder.use_cassette(
                'TestObjector.test_raise_api_exception'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            with pytest.raises(APIException) as excinfo:
                subreddit.mod.approve(self.reddit.submission('4b536h'))
            assert excinfo.value.error_type == 'USER_REQUIRED'
            assert str(excinfo.value) == message
