import pytest

from praw.models import Message, Redditor, Subreddit, SubredditMessage

from ... import IntegrationTest


class TestMessage(IntegrationTest):
    def test_attributes(self, reddit):
        reddit.read_only = False
        messages = list(reddit.inbox.messages())
        count = len(messages)
        while messages:
            message = messages.pop(0)
            messages.extend(message.replies)
            count -= 1
            try:
                assert message.author is None or isinstance(message.author, Redditor)
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

    def test_block(self, reddit):
        reddit.read_only = False
        message = None
        for item in reddit.inbox.messages():
            if item.author and item.author != pytest.placeholders.username:
                message = item
                break
        else:
            msg = "no message found"
            raise AssertionError(msg)
        message.block()

    def test_delete(self, reddit):
        reddit.read_only = False
        message = next(reddit.inbox.messages())
        message.delete()

    def test_mark_read(self, reddit):
        reddit.read_only = False
        message = None
        for item in reddit.inbox.unread():
            if isinstance(item, Message):
                message = item
                break
        else:
            msg = "no message found in unread"
            raise AssertionError(msg)
        message.mark_read()

    def test_mark_unread(self, reddit):
        reddit.read_only = False
        message = next(reddit.inbox.messages())
        message.mark_unread()

    def test_message_collapse(self, reddit):
        reddit.read_only = False
        message = next(reddit.inbox.messages())
        message.collapse()

    def test_message_uncollapse(self, reddit):
        reddit.read_only = False
        message = next(reddit.inbox.messages())
        message.uncollapse()

    def test_parent(self, reddit):
        reddit.read_only = False
        message = reddit.inbox.message("30rugdg")
        parent = message.parent
        assert isinstance(parent, Message)
        assert parent.fullname == message.parent_id

    def test_parent__from_inbox_listing(self, reddit):
        reddit.read_only = False
        message = next(reddit.inbox.sent(limit=1))
        parent = message.parent
        assert isinstance(parent, Message)
        assert parent.fullname == message.parent_id

    def test_reply(self, reddit):
        reddit.read_only = False
        message = next(reddit.inbox.messages())
        reply = message.reply(body="Message reply")
        assert reply.author == reddit.user.me()
        assert reply.body == "Message reply"
        assert reply.first_message_name == message.fullname
