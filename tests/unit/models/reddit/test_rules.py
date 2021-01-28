import pytest

from praw.models import Rule

from ... import UnitTest


class TestRules(UnitTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_empty_value(self):
        with pytest.raises(ValueError):
            Rule(self.reddit, self.subreddit, short_name="")

    def test_no_data(self):
        with pytest.raises(ValueError) as excinfo:
            Rule(self.reddit, self.subreddit)
        assert excinfo.value.args[0] == "Either short_name or _data needs to be given."

    def test_both_data(self):
        with pytest.raises(ValueError) as excinfo:
            Rule(self.reddit, self.subreddit, short_name="test", _data={})
        assert excinfo.value.args[0] == "Either short_name or _data needs to be given."

    def test_no_subreddit(self):
        rule = Rule(self.reddit, short_name="test")
        with pytest.raises(ValueError) as excinfo:
            getattr(rule, "subreddit")
        assert (
            excinfo.value.args[0]
            == "The Rule is missing a subreddit. File a bug report at PRAW."
        )
