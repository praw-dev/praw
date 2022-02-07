from datetime import datetime
from unittest import mock

from praw.models import ModmailMessage

from ... import IntegrationTest


class TestModmailConversation(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_archive(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.archive()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.state == 2

    @mock.patch("time.sleep", return_value=None)
    def test_highlight(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.highlight()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.is_highlighted

    @mock.patch("time.sleep", return_value=None)
    def test_mute(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.mute()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.user.mute_status["isMuted"]

    @mock.patch("time.sleep", return_value=None)
    def test_mute_duration(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("g46rw")
        with self.recorder.use_cassette("TestModmailConversation.test_mute_duration"):
            conversation.mute(num_days=7)
            conversation = self.reddit.subreddit("all").modmail("g46rw")
            assert conversation.user.mute_status["isMuted"]
            diff = datetime.fromisoformat(
                conversation.user.mute_status["endDate"]
            ) - datetime.fromisoformat(conversation.mod_actions[-1].date)
            assert diff.days == 6  # 6 here because it is not 7 whole days

    @mock.patch("time.sleep", return_value=None)
    def test_read(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.read()

    @mock.patch("time.sleep", return_value=None)
    def test_read__other_conversations(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("p8rp")
        other_conversation = self.reddit.subreddit("all").modmail("p8rr")
        with self.use_cassette():
            conversation.read(other_conversations=[other_conversation])

    def test_reply(self):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            reply = conversation.reply(body="A message")
        assert isinstance(reply, ModmailMessage)

    @mock.patch("time.sleep", return_value=None)
    def test_unarchive(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.unarchive()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.state == 1

    @mock.patch("time.sleep", return_value=None)
    def test_unhighlight(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.unhighlight()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert not conversation.is_highlighted

    @mock.patch("time.sleep", return_value=None)
    def test_unmute(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.unmute()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert not conversation.user.mute_status["isMuted"]

    @mock.patch("time.sleep", return_value=None)
    def test_unread(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("ik72")
        with self.use_cassette():
            conversation.unread()
            conversation = self.reddit.subreddit("all").modmail("ik72")
            assert conversation.last_unread is not None
