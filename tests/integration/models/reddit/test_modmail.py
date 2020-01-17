from praw.models import ModmailConversation, ModmailMessage
import json
import mock

from ... import IntegrationTest


class TestModmailConversation(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_archive(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_archive"
        ):
            conversation.archive()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.state == 2

    @mock.patch("time.sleep", return_value=None)
    def test_export(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("bbxec")
        with self.recorder.use_cassette("TestModmailConversation.test_export"):
            conversation._fetch()
            assert conversation._fetched
            conversation2 = ModmailConversation(
                self.reddit, _data=conversation.export()
            )
            assert conversation2.__dict__ == conversation.__dict__
            message = conversation.messages[0]
            message._fetch()
            assert message._fetched
            message2 = message.__class__(self.reddit, _data=message.export())
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_no_private(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("bbxec")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_export_no_private"
        ):
            conversation._fetch()
            data = conversation.export(remove_private=True)
            assert [key.startswith("_") for key, value in data.items()].count(
                True
            ) == 0
            conversation2 = ModmailConversation(self.reddit, _data=data)
            conversation2._fetched = True
            for key in conversation2.__dict__:
                assert (
                    conversation2.__dict__[key] == conversation.__dict__[key]
                )

    @mock.patch("time.sleep", return_value=None)
    def test_export_jsonify(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("bbxec")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_export_jsonify"
        ):
            conversation._fetch()
            jsondata = conversation.export(jsonify=True)
            assert isinstance(jsondata, str)
            assert [
                key.startswith("_") for key, _ in json.loads(jsondata).items()
            ].count(True) == 0
            conversation2 = ModmailConversation(
                self.reddit, _data=json.loads(jsondata)
            )
            conversation2._fetched = True
            assert conversation2.__dict__ == conversation.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_jsonify_with_private(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("bbxec")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_export_jsonify_with_private"
        ):
            conversation._fetch()
            jsondata = conversation.export(jsonify=True, remove_private=False)
            assert isinstance(jsondata, str)
            assert [
                key.startswith("_") for key, _ in json.loads(jsondata).items()
            ].count(True) > 0
            conversation2 = ModmailConversation(
                self.reddit, _data=json.loads(jsondata)
            )
            conversation2._fetched = True
            for key in conversation2.__dict__:
                assert (
                    conversation2.__dict__[key] == conversation.__dict__[key]
                ), key

    @mock.patch("time.sleep", return_value=None)
    def test_export_stringify(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("bbxec")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_export_stringify"
        ):
            conversation._fetch()
            assert conversation._fetched
            conversation2 = ModmailConversation(
                self.reddit, _data=conversation.export()
            )
            assert conversation2.__dict__ == conversation.__dict__
            message = conversation.messages[0]
            message._fetch()
            assert message._fetched
            message2 = message.__class__(
                self.reddit, _data=message.export(stringify=True)
            )
            assert message2.__dict__ == message.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_export_jsonify_stringify(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("bbxec")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_export_jsonify_stringify"
        ):
            conversation._fetch()
            jsondata = conversation.export(jsonify=True, stringify=True)
            assert isinstance(jsondata, str)
            assert [
                key.startswith("_") for key, _ in json.loads(jsondata).items()
            ].count(True) == 0
            conversation2 = ModmailConversation(
                self.reddit, _data=json.loads(jsondata)
            )
            conversation2._fetched = True
            assert conversation2.__dict__ == conversation.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_highlight(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_highlight"
        ):
            conversation.highlight()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.is_highlighted

    @mock.patch("time.sleep", return_value=None)
    def test_mute(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette("TestModmailConversation.test_mute"):
            conversation.mute()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.user.mute_status["isMuted"]

    @mock.patch("time.sleep", return_value=None)
    def test_read(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette("TestModmailConversation.test_read"):
            conversation.read()

    @mock.patch("time.sleep", return_value=None)
    def test_read__other_conversations(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("p8rp")
        other_conversation = self.reddit.subreddit("all").modmail("p8rr")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_read__other_conversations"
        ):
            conversation.read(other_conversations=[other_conversation])

    def test_reply(self):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette("TestModmailConversation.test_reply"):
            reply = conversation.reply("A message")
        assert isinstance(reply, ModmailMessage)

    @mock.patch("time.sleep", return_value=None)
    def test_unarchive(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_unarchive"
        ):
            conversation.unarchive()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.state == 1

    @mock.patch("time.sleep", return_value=None)
    def test_unhighlight(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette(
            "TestModmailConversation.test_unhighlight"
        ):
            conversation.unhighlight()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert not conversation.is_highlighted

    @mock.patch("time.sleep", return_value=None)
    def test_unmute(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette("TestModmailConversation.test_unmute"):
            conversation.unmute()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert not conversation.user.mute_status["isMuted"]

    @mock.patch("time.sleep", return_value=None)
    def test_unread(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.recorder.use_cassette("TestModmailConversation.test_unread"):
            conversation.unread()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.last_unread is not None
