"""Test praw.models.redditor."""

import pytest
from prawcore import Forbidden

from praw.exceptions import RedditAPIException
from praw.models import Comment, Submission

from ... import IntegrationTest


class TestRedditor(IntegrationTest):
    FRIEND = "PyAPITestUser3"
    FRIEND_FULLNAME = "t2_6c1xj"

    def test_block(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(self.FRIEND)
        redditor.block()

    def test_friend(self, reddit):
        reddit.read_only = False
        reddit.redditor(self.FRIEND.lower()).friend()

    def test_friend__with_note__no_gold(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            reddit.redditor(self.FRIEND.lower()).friend(note="praw")
        assert "GOLD_REQUIRED" == excinfo.value.error_type

    def test_friend_info(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(self.FRIEND).friend_info()
        assert self.FRIEND == redditor
        assert "date" in redditor.__dict__
        assert "created_utc" not in redditor.__dict__
        assert hasattr(redditor, "created_utc")

    def test_fullname_init(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(fullname=self.FRIEND_FULLNAME)
        assert redditor.name == self.FRIEND

    def test_gild__no_creddits(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            reddit.redditor("subreddit_stats").gild()
        assert "INSUFFICIENT_CREDDITS" == excinfo.value.error_type

    def test_message(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("subreddit_stats")
        redditor.message(subject="PRAW test", message="This is a test from PRAW")

    def test_message_from_subreddit(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("subreddit_stats")
        redditor.message(
            subject="PRAW test",
            message="This is a test from PRAW",
            from_subreddit=pytest.placeholders.test_subreddit,
        )

    def test_moderated(self, reddit):
        redditor = reddit.redditor("spez")
        redditor_no_mod = reddit.redditor("ArtemisHelper")
        moderated = redditor.moderated()
        assert len(moderated) > 0
        assert len(moderated[0].name) > 0
        not_moderated = redditor_no_mod.moderated()
        assert len(not_moderated) == 0

    def test_multireddits(self, reddit):
        redditor = reddit.redditor("kjoneslol")
        for multireddit in redditor.multireddits():
            if "sfwpornnetwork" == multireddit.name:
                break
        else:
            assert False, "sfwpornnetwork not found in multireddits"

    def test_notes__subreddits(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("Watchful1")
        notes = list(redditor.notes.subreddits("subtestbot1", "subtestbot2"))
        assert len(notes) == 2
        assert notes[0].user == redditor
        assert notes[1] is None

    def test_stream__comments(self, reddit):
        generator = reddit.redditor("AutoModerator").stream.comments()
        for i in range(101):
            assert isinstance(next(generator), Comment)

    def test_stream__submissions(self, reddit):
        generator = reddit.redditor("AutoModerator").stream.submissions()
        for i in range(101):
            assert isinstance(next(generator), Submission)

    def test_trophies(self, reddit):
        redditor = reddit.redditor("spez")
        trophies = redditor.trophies()
        assert len(trophies) > 0
        assert len(trophies[0].name) > 0

    def test_trophies__user_not_exist(self, reddit):
        redditor = reddit.redditor("thisusershouldnotexist")
        with pytest.raises(RedditAPIException) as excinfo:
            redditor.trophies()
        assert "USER_DOESNT_EXIST" == excinfo.value.error_type

    def test_unblock(self, reddit):
        reddit.read_only = False
        redditor = reddit.user.blocked()[0]
        redditor.unblock()

    def test_unfriend(self, reddit):
        reddit.read_only = False
        redditor = reddit.user.friends()[0]
        assert redditor.unfriend() is None


class TestRedditorListings(IntegrationTest):
    def test_comments__controversial(self, reddit):
        redditor = reddit.redditor("spez")
        comments = list(redditor.comments.controversial())
        assert len(comments) == 100

    def test_comments__hot(self, reddit):
        redditor = reddit.redditor("spez")
        comments = list(redditor.comments.hot())
        assert len(comments) == 100

    def test_comments__new(self, reddit):
        redditor = reddit.redditor("spez")
        comments = list(redditor.comments.new())
        assert len(comments) == 100

    def test_comments__top(self, reddit):
        redditor = reddit.redditor("spez")
        comments = list(redditor.comments.top())
        assert len(comments) == 100

    def test_controversial(self, reddit):
        redditor = reddit.redditor("spez")
        items = list(redditor.controversial())
        assert len(items) == 100

    def test_downvoted(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(reddit.config.username)
        submissions = list(redditor.downvoted())
        assert len(submissions) > 0

    def test_downvoted__in_read_only_mode(self, reddit):
        redditor = reddit.redditor(reddit.config.username)
        with pytest.raises(Forbidden):
            list(redditor.downvoted())

    def test_downvoted__other_user(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("spez")
        with pytest.raises(Forbidden):
            list(redditor.downvoted())

    def test_gilded(self, reddit):
        redditor = reddit.redditor("spez")
        items = list(redditor.gilded(limit=50))
        assert len(items) == 50

    def test_gildings(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(reddit.config.username)
        items = list(redditor.gildings())
        assert isinstance(items, list)

    def test_gildings__in_read_only_mode(self, reddit):
        redditor = reddit.redditor(reddit.config.username)
        with pytest.raises(Forbidden):
            list(redditor.gildings())

    def test_gildings__other_user(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("spez")
        with pytest.raises(Forbidden):
            list(redditor.gildings())

    def test_hidden(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(reddit.config.username)
        submissions = list(redditor.hidden())
        assert len(submissions) > 0

    def test_hidden__in_read_only_mode(self, reddit):
        redditor = reddit.redditor(reddit.config.username)
        with pytest.raises(Forbidden):
            list(redditor.hidden())

    def test_hidden__other_user(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("spez")
        with pytest.raises(Forbidden):
            list(redditor.hidden())

    def test_hot(self, reddit):
        redditor = reddit.redditor("spez")
        items = list(redditor.hot())
        assert len(items) == 100

    def test_new(self, reddit):
        redditor = reddit.redditor("spez")
        items = list(redditor.new())
        assert len(items) == 100

    def test_saved(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(reddit.config.username)
        items = list(redditor.saved())
        assert len(items) > 0

    def test_saved__in_read_only_mode(self, reddit):
        redditor = reddit.redditor(reddit.config.username)
        with pytest.raises(Forbidden):
            list(redditor.saved())

    def test_saved__other_user(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("spez")
        with pytest.raises(Forbidden):
            list(redditor.saved())

    def test_submissions__controversial(self, reddit):
        redditor = reddit.redditor("spladug")
        submissions = list(redditor.submissions.controversial())
        assert len(submissions) == 100

    def test_submissions__hot(self, reddit):
        redditor = reddit.redditor("spez")
        submissions = list(redditor.submissions.hot())
        assert len(submissions) == 100

    def test_submissions__new(self, reddit):
        redditor = reddit.redditor("spez")
        submissions = list(redditor.submissions.new())
        assert len(submissions) == 100

    def test_submissions__top(self, reddit):
        redditor = reddit.redditor("spladug")
        submissions = list(redditor.submissions.top())
        assert len(submissions) == 100

    def test_top(self, reddit):
        redditor = reddit.redditor("spez")
        items = list(redditor.top())
        assert len(items) == 100

    def test_trust_and_distrust(self, reddit):
        reddit.read_only = False
        reddit.redditor("PyAPITestUser3").trust()
        redditor = reddit.user.trusted()[0]
        redditor.distrust()

    def test_trust_blocked_user(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("kn0thing")
        redditor.block()
        with pytest.raises(RedditAPIException) as excinfo:
            redditor.trust()
        assert "CANT_WHITELIST_AN_ENEMY" == excinfo.value.error_type

    def test_upvoted(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(reddit.config.username)
        submissions = list(redditor.upvoted())
        assert len(submissions) > 0

    def test_upvoted__in_read_only_mode(self, reddit):
        redditor = reddit.redditor(reddit.config.username)
        with pytest.raises(Forbidden):
            list(redditor.upvoted())

    def test_upvoted__other_user(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor("spez")
        with pytest.raises(Forbidden):
            list(redditor.upvoted())
