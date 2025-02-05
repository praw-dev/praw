"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from praw import Reddit
from praw.exceptions import WebSocketException
from praw.models.reddit.user_subreddit import UserSubreddit
from praw.util.token_manager import FileTokenManager

from . import UnitTest


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecation(UnitTest):
    def test_conversations_after_argument(self, reddit):
        with pytest.deprecated_call():
            reddit.subreddit("all").modmail.conversations(after="after")

    def test_reddit_token_manager(self):
        with pytest.raises(DeprecationWarning):
            Reddit(
                token_manager=FileTokenManager("name"),
                client_id="dummy",
                client_secret=None,
                redirect_uri="dummy",
                user_agent="dummy",
            )

    def test_reddit_user_me_read_only(self, reddit):
        with pytest.raises(DeprecationWarning):
            reddit.user.me()

    def test_subreddit_rules_call(self, reddit):
        with pytest.raises(DeprecationWarning) as excinfo:
            reddit.subreddit("test").rules()
        assert (
            excinfo.value.args[0]
            == "Calling SubredditRules to get a list of rules is deprecated. Remove the parentheses to use the iterator. View the PRAW documentation on how to change the code in order to use the iterator (https://praw.readthedocs.io/en/latest/code_overview/other/subredditrules.html#praw.models.reddit.rules.SubredditRules.__call__)."
        )

    def test_user_subreddit_as_dict(self):
        user_subreddit = UserSubreddit(None, display_name="test")
        with pytest.deprecated_call() as warning_info:
            display_name = user_subreddit["display_name"]
            assert display_name == "test"
            assert (
                warning_info.list[0].message.args[0]
                == "'Redditor.subreddit' is no longer a dict and is now an UserSubreddit object. Accessing attributes using string indices is deprecated."
            )
            assert user_subreddit.keys() == user_subreddit.__dict__.keys()
            assert (
                warning_info.list[1].message.args[0]
                == "'Redditor.subreddit' is no longer a dict and is now an UserSubreddit object. Using 'keys' is deprecated and will be removed in PRAW 8."
            )
