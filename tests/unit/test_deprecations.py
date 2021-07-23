"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from praw import Reddit
from praw.exceptions import APIException, WebSocketException
from praw.models.reddit.user_subreddit import UserSubreddit
from praw.util.token_manager import FileTokenManager

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
            == "Calling SubredditRules to get a list of rules is deprecated. Remove the parentheses to use the iterator. View the PRAW documentation on how to change the code in order to use the iterator (https://praw.readthedocs.io/en/latest/code_overview/other/subredditrules.html#praw.models.reddit.rules.SubredditRules.__call__)."
        )

    def test_web_socket_exception_attribute(self):
        exc = WebSocketException("Test", Exception("Test"))
        with pytest.raises(DeprecationWarning) as excinfo:
            _ = exc.original_exception
        assert (
            excinfo.value.args[0]
            == "Accessing the attribute original_exception is deprecated. Please rewrite your code in such a way that this attribute does not need to be used. It will be removed in PRAW 8.0."
        )

    def test_gold_method(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddits.gold()
            assert (
                excinfo.value.args[0]
                == "`subreddits.gold` has be renamed to `subreddits.premium`."
            )

    def test_gild_method(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.submission("1234").gild()
            assert excinfo.value.args[0] == "`.gild` has been renamed to `.award`."

    def test_reddit_token_manager(self):
        with pytest.raises(DeprecationWarning):
            Reddit(
                client_id="dummy",
                client_secret=None,
                redirect_uri="dummy",
                user_agent="dummy",
                token_manager=FileTokenManager("name"),
            )

    def test_reddit_user_me_read_only(self):
        with pytest.raises(DeprecationWarning):
            self.reddit.user.me()

    def test_user_subreddit_as_dict(self):
        user_subreddit = UserSubreddit(None, display_name="test")
        with pytest.deprecated_call() as warning_info:
            display_name = user_subreddit["display_name"]
            assert display_name == "test"
            assert (
                warning_info.list[0].message.args[0]
                == "`Redditor.subreddit` is no longer a dict and is now an `UserSubreddit` object. Accessing attributes using string indices is deprecated."
            )
            assert user_subreddit.keys() == user_subreddit.__dict__.keys()
            assert (
                warning_info.list[1].message.args[0]
                == "`Redditor.subreddit` is no longer a dict and is now an `UserSubreddit` object. Using `keys` is deprecated and will be removed in PRAW 8."
            )
