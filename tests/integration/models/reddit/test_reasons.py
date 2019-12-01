from praw.exceptions import ClientException
from praw.models import Reason
import mock
import pytest

from ... import IntegrationTest


class TestReason(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test__fetch(self, _):
        self.reddit.read_only = False
        reason = self.subreddit.reasons["110nhral8vygf"]
        with self.recorder.use_cassette("TestReason.test__fetch"):
            assert reason.title.startswith("Be Kind")

    @mock.patch("time.sleep", return_value=None)
    def test__fetch__invalid_reason(self, _):
        self.reddit.read_only = False
        reason = self.subreddit.reasons["invalid"]
        with self.recorder.use_cassette(
            "TestReason.test__fetch__invalid_reason"
        ):
            with pytest.raises(ClientException) as excinfo:
                reason.title
            assert str(excinfo.value) == (
                "/r/{} does not have the reason {}".format(
                    self.subreddit, "invalid"
                )
            )


class TestSubredditReasons(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubredditReasons.test__iter"):
            count = 0
            for reason in self.subreddit.reasons:
                assert isinstance(reason, Reason)
                count += 1
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubredditReasons.test_add"):
            reason = self.subreddit.reasons.add("test", "Test")
            assert isinstance(reason, Reason)

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubredditReasons.test_update"):
            reason = next(x for x in self.subreddit.reasons)
            self.subreddit.reasons.update(
                reason.id, "PRAW updated", "New Message"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubredditReasons.test_delete"):
            reason = next(x for x in self.subreddit.reasons)
            self.subreddit.reasons.delete(reason.id)
