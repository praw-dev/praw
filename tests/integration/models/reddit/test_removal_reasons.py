from unittest import mock

import pytest

from praw.exceptions import ClientException
from praw.models import RemovalReason

from ... import IntegrationTest


class TestRemovalReason(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test__fetch(self, _):
        self.reddit.read_only = False
        reason = self.subreddit.mod.removal_reasons["110nhral8vygf"]
        with self.use_cassette():
            assert reason.title.startswith("Be Kind")

    @mock.patch("time.sleep", return_value=None)
    def test__fetch_int(self, _):
        self.reddit.read_only = False
        with self.use_cassette("TestRemovalReason.test__fetch"):
            reason = self.subreddit.mod.removal_reasons[0]
            assert isinstance(reason, RemovalReason)

    @mock.patch("time.sleep", return_value=None)
    def test__fetch_slice(self, _):
        self.reddit.read_only = False
        with self.use_cassette("TestRemovalReason.test__fetch"):
            reasons = self.subreddit.mod.removal_reasons[-3:]
            assert len(reasons) == 3
            for reason in reasons:
                assert isinstance(reason, RemovalReason)

    @mock.patch("time.sleep", return_value=None)
    def test__fetch__invalid_reason(self, _):
        self.reddit.read_only = False
        reason = self.subreddit.mod.removal_reasons["invalid"]
        with self.use_cassette():
            with pytest.raises(ClientException) as excinfo:
                reason.title
            assert str(excinfo.value) == (
                f"Subreddit {self.subreddit} does not have the removal reason invalid"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            reason = self.subreddit.mod.removal_reasons["110nhk2cgmaxy"]
            reason.update(message="New Message", title="New Title")

    @mock.patch("time.sleep", return_value=None)
    def test_update_empty(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            reason = self.subreddit.mod.removal_reasons[0]
            reason.update()

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            reason = self.subreddit.mod.removal_reasons["110nhyk34m01d"]
            reason.delete()


class TestSubredditRemovalReasons(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for reason in self.subreddit.mod.removal_reasons:
                assert isinstance(reason, RemovalReason)
                count += 1
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            reason = self.subreddit.mod.removal_reasons.add("test", "Test")
            assert isinstance(reason, RemovalReason)
