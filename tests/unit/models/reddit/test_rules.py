import pytest

from praw.models import Rule, Subreddit

from ... import UnitTest


class TestRules(UnitTest):
    @property
    def subreddit(self):
        return Subreddit(None, pytest.placeholders.test_subreddit)

    def test_both_data(self, reddit):
        with pytest.raises(ValueError) as excinfo:
            Rule(reddit, self.subreddit, short_name="test", _data={})
        assert excinfo.value.args[0] == "Either short_name or _data needs to be given."

    def test_empty_value(self, reddit):
        with pytest.raises(ValueError):
            Rule(reddit, self.subreddit, short_name="")

    def test_no_data(self, reddit):
        with pytest.raises(ValueError) as excinfo:
            Rule(reddit, self.subreddit)
        assert excinfo.value.args[0] == "Either short_name or _data needs to be given."

    def test_no_subreddit(self, reddit):
        rule = Rule(reddit, short_name="test")
        with pytest.raises(ValueError) as excinfo:
            getattr(rule, "subreddit")
        assert (
            excinfo.value.args[0]
            == "The Rule is missing a subreddit. File a bug report at PRAW."
        )
