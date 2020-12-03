from unittest import mock

import pytest

from praw.models import Message, Redditor, Subreddit, SubredditMessage

from ... import IntegrationTest


class TestMessage(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_attributes(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            messages = list(self.reddit.inbox.messages())
            count = len(messages)
            while messages:
                message = messages.pop(0)
                messages.extend(message.replies)
                count -= 1
                try:
                    assert message.author is None or isinstance(
                        message.author, Redditor
                    )
                    assert isinstance(message.dest, (Redditor, Subreddit))
                    assert isinstance(message.replies, list)
                    assert message.subreddit is None or isinstance(
                        message.subreddit, Subreddit
                    )
                except Exception:
                    import pprint

                    pprint.pprint(vars(message))
                    raise
        assert count < 0

    @mock.patch("time.sleep", return_value=None)
    def test_block(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = None
            for item in self.reddit.inbox.messages():
                if item.author and item.author != pytest.placeholders.username:
                    message = item
                    break
            else:
                assert False, "no message found"
            message.block()

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = next(self.reddit.inbox.messages())
            message.delete()

    @mock.patch("time.sleep", return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = None
            for item in self.reddit.inbox.unread():
                if isinstance(item, Message):
                    message = item
                    break
            else:
                assert False, "no message found in unread"
            message.mark_read()

    @mock.patch("time.sleep", return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = next(self.reddit.inbox.messages())
            message.mark_unread()

    @mock.patch("time.sleep", return_value=None)
    def test_message_collapse(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = next(self.reddit.inbox.messages())
            message.collapse()

    @mock.patch("time.sleep", return_value=None)
    def test_message_uncollapse(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = next(self.reddit.inbox.messages())
            message.uncollapse()

    @mock.patch("time.sleep", return_value=None)
    def test_reply(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            message = next(self.reddit.inbox.messages())
            reply = message.reply("Message reply")
            assert reply.author == self.reddit.config.username
            assert reply.body == "Message reply"
            assert reply.first_message_name == message.fullname


class TestSubredditMessage(IntegrationTest):
    def test_mute(self):
        self.reddit.read_only = False
        with self.use_cassette():
            message = SubredditMessage(self.reddit, _data={"id": "5yr8id"})
            message.mute()

    def test_unmute(self):
        self.reddit.read_only = False
        with self.use_cassette():
            message = SubredditMessage(self.reddit, _data={"id": "5yr8id"})
            message.unmute()
