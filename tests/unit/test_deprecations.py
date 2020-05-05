"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from praw.exceptions import APIException

from . import UnitTest


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecation(UnitTest):
    def test_validate_on_submit(self):
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit
        self.reddit.validate_on_submit = True
        assert self.reddit.validate_on_submit
        self.reddit.validate_on_submit = False
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit

    def test_api_exception(self):
        exc = APIException(["test", "testing", "test"])
        with pytest.raises(DeprecationWarning):
            exc.error_type
        with pytest.raises(DeprecationWarning):
            exc.message
        with pytest.raises(DeprecationWarning):
            exc.field

    def test_subreddit_rules_call(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").rules()
        assert (
            excinfo.value.args[0]
            == "Calling SubredditRules to get a list of rules is deprecated. "
            "Remove the parentheses to use the iterator. View the "
            "PRAW documentation on how to change the code in order to use the"
            "iterator (https://praw.readthedocs.io/en/latest/code_overview"
            "/other/subredditrules.html#praw.models.reddit.rules."
            "SubredditRules.__call__)."
        )
