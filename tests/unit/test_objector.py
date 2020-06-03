import pytest

from praw.exceptions import ClientException, RedditAPIException

from . import UnitTest


class TestObjector(UnitTest):
    def test_objectify_returns_None_for_None(self):
        assert self.reddit._objector.objectify(None) is None

    def test_parse_error(self):
        objector = self.reddit._objector
        assert objector.parse_error({}) is None
        assert objector.parse_error([]) is None
        assert objector.parse_error({"asdf": 1}) is None

        error_response = {
            "json": {"errors": [["USER_REQUIRED", "Please log in to do that.", None]]}
        }
        error = objector.parse_error(error_response)
        assert isinstance(error, RedditAPIException)

        error_response = {"json": {"errors": []}}
        with pytest.raises(ClientException):
            objector.parse_error(error_response)

        error_response = {
            "json": {
                "errors": [
                    ["USER_REQUIRED", "Please log in to do that.", None],
                    ["NO_SUBJECT", "please enter a subject", "subject"],
                ]
            }
        }
        assert isinstance(objector.parse_error(error_response), RedditAPIException)

    def test_check_error(self):
        objector = self.reddit._objector
        objector.check_error({"asdf": 1})

        error_response = {
            "json": {"errors": [["USER_REQUIRED", "Please log in to do that.", None]]}
        }
        with pytest.raises(RedditAPIException):
            objector.check_error(error_response)
