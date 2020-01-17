from praw.models import Message, Redditor, Subreddit, SubredditMessage
import json
import mock
import pytest

from ... import IntegrationTest


class TestMessage(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_attributes(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_attributes"):
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
        with self.recorder.use_cassette("TestMessage.test_block"):
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
        with self.recorder.use_cassette("TestMessage.test_delete"):
            message = next(self.reddit.inbox.messages())
            message.delete()

    @mock.patch("time.sleep", return_value=None)
    def test_export(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_export"):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            message2 = Message(self.reddit, message.export())
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_no_private(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_export_no_private"):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            data = message.export(remove_private=True)
            assert [key.startswith("_") for key, value in data.items()].count(
                True
            ) == 0
            message2 = Message(self.reddit, _data=data)
            for key in message2.__dict__:
                assert message2.__dict__[key] == message.__dict__[key]

    @mock.patch("time.sleep", return_value=None)
    def test_export_jsonify(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_export_jsonify"):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            jsondata = message.export(jsonify=True)
            assert isinstance(jsondata, str)
            assert [
                key.startswith("_") for key, _ in json.loads(jsondata).items()
            ].count(True) == 0
            message2 = Message(self.reddit, _data=json.loads(jsondata))
            assert message2._fetched
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_jsonify_with_private(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestMessage.test_export_jsonify_with_private"
        ):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            jsondata = message.export(jsonify=True, remove_private=False)
            assert isinstance(jsondata, str)
            assert [
                key.startswith("_") for key, _ in json.loads(jsondata).items()
            ].count(True) > 0
            message2 = Message(self.reddit, _data=json.loads(jsondata))
            assert message2._fetched
            for key in message2.__dict__:
                assert message2.__dict__[key] == message.__dict__[key]

    @mock.patch("time.sleep", return_value=None)
    def test_export_stringify(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_export_stringify"):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            message2 = Message(self.reddit, message.export(stringify=True))
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_jsonify_stringify(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestMessage.test_export_jsonify_stringify"
        ):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            jsondata = message.export(jsonify=True, stringify=True)
            assert isinstance(jsondata, str)
            assert [
                key.startswith("_") for key, _ in json.loads(jsondata).items()
            ].count(True) == 0
            message2 = Message(self.reddit, _data=json.loads(jsondata))
            assert message2._fetched
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_to_redditor(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_export_redditor"):
            message = next(self.reddit.inbox.messages())
            message._fetch()
            assert message._fetched
            message2 = Message(self.reddit, message.export())
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_from_subreddit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestMessage.test_export_from_subreddit"
        ):
            message = self.reddit.inbox.message("ll216w")
            message._fetch()
            assert message._fetched
            message2 = Message(self.reddit, message.export())
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_to_subreddit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestMessage.test_export_to_subreddit"
        ):
            message = self.reddit.inbox.message("ll22wt")
            message._fetch()
            assert message._fetched
            message2 = Message(self.reddit, message.export())
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_replies(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_export_replies"):
            message = self.reddit.inbox.message("kzwk3j")
            message._fetch()
            assert message._fetched
            message2 = Message(self.reddit, message.export())
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_mark_read"):
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
        with self.recorder.use_cassette("TestMessage.test_mark_unread"):
            message = next(self.reddit.inbox.messages())
            message.mark_unread()

    @mock.patch("time.sleep", return_value=None)
    def test_message_collapse(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_message_collapse"):
            message = next(self.reddit.inbox.messages())
            message.collapse()

    @mock.patch("time.sleep", return_value=None)
    def test_message_uncollapse(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_message_uncollapse"):
            message = next(self.reddit.inbox.messages())
            message.uncollapse()

    @mock.patch("time.sleep", return_value=None)
    def test_reply(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestMessage.test_reply"):
            message = next(self.reddit.inbox.messages())
            reply = message.reply("Message reply")
            assert reply.author == self.reddit.config.username
            assert reply.body == "Message reply"
            assert reply.first_message_name == message.fullname


class TestSubredditMessage(IntegrationTest):
    def test_mute(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubredditMessage.test_mute"):
            message = SubredditMessage(self.reddit, _data={"id": "5yr8id"})
            message.mute()

    def test_unmute(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubredditMessage.test_unmute"):
            message = SubredditMessage(self.reddit, _data={"id": "5yr8id"})
            message.unmute()
