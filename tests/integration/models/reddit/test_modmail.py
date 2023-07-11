from datetime import datetime

from praw.models import ModmailMessage

from ... import IntegrationTest


class TestModmailConversation(IntegrationTest):
    def test_archive(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.archive()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert conversation.state == 2

    def test_highlight(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.highlight()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert conversation.is_highlighted

    def test_mute(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.mute()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert conversation.user.mute_status["isMuted"]

    def test_mute_duration(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("g46rw")
        conversation.mute(num_days=7)
        conversation = reddit.subreddit("all").modmail("g46rw")
        assert conversation.user.mute_status["isMuted"]
        diff = datetime.fromisoformat(
            conversation.user.mute_status["endDate"]
        ) - datetime.fromisoformat(conversation.mod_actions[-1].date)
        assert diff.days == 6  # 6 here because it is not 7 whole days

    def test_read(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.read()

    def test_read__other_conversations(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("p8rp")
        other_conversation = reddit.subreddit("all").modmail("p8rr")
        conversation.read(other_conversations=[other_conversation])

    def test_reply(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        reply = conversation.reply(body="A message")
        assert isinstance(reply, ModmailMessage)

    def test_reply__internal(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("1mahha")
        reply = conversation.reply(internal=True, body="A message")
        assert isinstance(reply, ModmailMessage)

    def test_unarchive(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.unarchive()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert conversation.state == 1

    def test_unhighlight(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.unhighlight()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert not conversation.is_highlighted

    def test_unmute(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.unmute()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert not conversation.user.mute_status["isMuted"]

    def test_unread(self, reddit):
        reddit.read_only = False
        conversation = reddit.subreddit("all").modmail("ik72")
        conversation.unread()
        conversation = reddit.subreddit("all").modmail("ik72")
        assert conversation.last_unread is not None
