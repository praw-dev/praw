"""Test praw.objector."""
import pytest

from praw.exceptions import APIException

from . import IntegrationTest


class TestObjector(IntegrationTest):
    def test_raise_api_exception(self):
        message = "USER_REQUIRED: 'Please log in to do that.'"
        with self.recorder.use_cassette(
            "TestObjector.test_raise_api_exception"
        ):
            submission = self.reddit.submission("4b536h")
            with pytest.raises(APIException) as excinfo:
                submission.mod.approve()
            assert excinfo.value[0].error_type == "USER_REQUIRED"
            assert str(excinfo.value[0]) == message
