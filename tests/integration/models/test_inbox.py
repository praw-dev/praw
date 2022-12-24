"""Test praw.models.inbox."""

import pytest
from prawcore import Forbidden

from praw.models import Comment, Message, Redditor, Subreddit

from .. import IntegrationTest


class TestInbox(IntegrationTest):
    def test_all(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.all():
            assert isinstance(item, Comment) or isinstance(item, Message)
            count += 1
        assert count == 100

    def test_all__with_limit(self, reddit):
        reddit.read_only = False
        assert len(list(reddit.inbox.all(limit=128))) == 128

    def test_comment_replies(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.comment_replies(limit=64):
            assert isinstance(item, Comment)
            assert item.parent_id.startswith(reddit.config.kinds["comment"])
            count += 1
        assert count == 64

    def test_comment_reply__refresh(self, reddit):
        reddit.read_only = False
        comment = next(reddit.inbox.comment_replies())
        saved_id = comment.id
        assert isinstance(comment, Comment)
        comment.refresh()
        assert saved_id == comment.id

    def test_mark_all_read(self, reddit):
        reddit.read_only = False
        reddit.inbox.mark_unread(list(reddit.inbox.all(limit=2)))
        reddit.inbox.mark_all_read()
        assert not list(reddit.inbox.unread())

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_mark_read(self, reddit):
        reddit.read_only = False
        reddit.inbox.mark_read(list(reddit.inbox.unread()))

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_mark_unread(self, reddit):
        reddit.read_only = False
        reddit.inbox.mark_unread(list(reddit.inbox.all()))

    def test_mention__refresh(self, reddit):
        reddit.read_only = False
        mention = next(reddit.inbox.mentions())
        assert isinstance(mention, Comment)
        mention.refresh()

    def test_mentions(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.mentions(limit=16):
            assert isinstance(item, Comment)
            count += 1
        assert count > 0

    def test_message(self, reddit):
        reddit.read_only = False
        message = reddit.inbox.message("6vzfan")
        assert message.name.split("_", 1)[1] == "6vzfan"
        assert isinstance(message, Message)
        assert isinstance(message.author, Redditor)
        assert isinstance(message.dest, Subreddit)
        assert message.replies == []
        assert isinstance(message.subreddit, Subreddit)

    def test_message__unauthorized(self, reddit):
        reddit.read_only = False
        with pytest.raises(Forbidden):
            reddit.inbox.message("6i8om7")

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_message_collapse(self, reddit):
        reddit.read_only = False
        reddit.inbox.collapse(list(reddit.inbox.messages()))

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_message_uncollapse(self, reddit):
        reddit.read_only = False
        reddit.inbox.uncollapse(list(reddit.inbox.messages()))

    def test_messages(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.messages(limit=64):
            assert isinstance(item, Message)
            count += 1
        assert count == 64

    def test_sent(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.sent(limit=64):
            assert isinstance(item, Message)
            assert item.author == reddit.config.username
            count += 1
        assert count == 64

    def test_stream(self, reddit):
        reddit.read_only = False
        item = next(reddit.inbox.stream())
        assert isinstance(item, Comment) or isinstance(item, Message)

    def test_submission_replies(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.submission_replies(limit=64):
            assert isinstance(item, Comment)
            assert item.parent_id.startswith(reddit.config.kinds["submission"])
            count += 1
        assert count == 64

    def test_unread(self, reddit):
        reddit.read_only = False
        count = 0
        for item in reddit.inbox.unread(limit=64):
            count += 1
        assert count == 64
