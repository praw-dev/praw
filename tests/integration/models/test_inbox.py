"""Test praw.models.inbox."""
from unittest import mock

import pytest
from prawcore import Forbidden

from praw.models import Comment, Message, Redditor, Subreddit

from .. import IntegrationTest


class TestInbox(IntegrationTest):
    def test_all(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.all():
                assert isinstance(item, Comment) or isinstance(item, Message)
                count += 1
            assert count == 100

    @mock.patch("time.sleep", return_value=None)
    def test_all__with_limit(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            assert len(list(self.reddit.inbox.all(limit=128))) == 128

    def test_comment_replies(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.comment_replies(limit=64):
                assert isinstance(item, Comment)
                assert item.parent_id.startswith(self.reddit.config.kinds["comment"])
                count += 1
            assert count == 64

    @mock.patch("time.sleep", return_value=None)
    def test_comment_reply__refresh(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = next(self.reddit.inbox.comment_replies())
            saved_id = comment.id
            assert isinstance(comment, Comment)
            comment.refresh()
            assert saved_id == comment.id

    @mock.patch("time.sleep", return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.use_cassette(match_requests_on=["uri", "method", "body"]):
            self.reddit.inbox.mark_read(list(self.reddit.inbox.unread()))

    @mock.patch("time.sleep", return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.use_cassette(match_requests_on=["uri", "method", "body"]):
            self.reddit.inbox.mark_unread(list(self.reddit.inbox.all()))

    @mock.patch("time.sleep", return_value=None)
    def test_mention__refresh(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            mention = next(self.reddit.inbox.mentions())
            assert isinstance(mention, Comment)
            mention.refresh()

    def test_mentions(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.mentions(limit=16):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_message(self):
        self.reddit.read_only = False
        with self.use_cassette():
            message = self.reddit.inbox.message("6vzfan")
        assert message.name.split("_", 1)[1] == "6vzfan"
        assert isinstance(message, Message)
        assert isinstance(message.author, Redditor)
        assert isinstance(message.dest, Subreddit)
        assert message.replies == []
        assert isinstance(message.subreddit, Subreddit)

    def test_message__unauthorized(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(Forbidden):
                self.reddit.inbox.message("6i8om7")

    @mock.patch("time.sleep", return_value=None)
    def test_message_collapse(self, _):
        self.reddit.read_only = False
        with self.use_cassette(match_requests_on=["uri", "method", "body"]):
            self.reddit.inbox.collapse(list(self.reddit.inbox.messages()))

    @mock.patch("time.sleep", return_value=None)
    def test_message_uncollapse(self, _):
        self.reddit.read_only = False
        with self.use_cassette(match_requests_on=["uri", "method", "body"]):
            self.reddit.inbox.uncollapse(list(self.reddit.inbox.messages()))

    def test_messages(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.messages(limit=64):
                assert isinstance(item, Message)
                count += 1
            assert count == 64

    def test_sent(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.sent(limit=64):
                assert isinstance(item, Message)
                assert item.author == self.reddit.config.username
                count += 1
            assert count == 64

    @mock.patch("time.sleep", return_value=None)
    def test_stream(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            item = next(self.reddit.inbox.stream())
            assert isinstance(item, Comment) or isinstance(item, Message)

    def test_submission_replies(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.submission_replies(limit=64):
                assert isinstance(item, Comment)
                assert item.parent_id.startswith(self.reddit.config.kinds["submission"])
                count += 1
            assert count == 64

    @mock.patch("time.sleep", return_value=None)
    def test_unread(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.inbox.unread(limit=64):
                count += 1
            assert count == 64
