"""Test praw.models.user."""
from unittest import mock

import prawcore.exceptions
import pytest

from praw.exceptions import RedditAPIException
from praw.models import Multireddit, Redditor, Submission, Subreddit

from .. import IntegrationTest


class TestUser(IntegrationTest):
    def test_blocked(self):
        self.reddit.read_only = False
        with self.use_cassette():
            blocked = self.reddit.user.blocked()
        assert len(blocked) > 0
        assert all(isinstance(user, Redditor) for user in blocked)

    def test_blocked_fullname(self):
        self.reddit.read_only = False
        with self.use_cassette():
            blocked = next(iter(self.reddit.user.blocked()))
            assert blocked.fullname.startswith("t2_")
            assert not blocked.fullname.startswith("t2_t2")

    def test_contributor_subreddits(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for subreddit in self.reddit.user.contributor_subreddits():
                assert isinstance(subreddit, Subreddit)
                count += 1
            assert count > 0

    def test_friends(self):
        self.reddit.read_only = False
        with self.use_cassette():
            friends = self.reddit.user.friends()
        assert len(friends) > 0
        assert all(isinstance(friend, Redditor) for friend in friends)

    @mock.patch("time.sleep", return_value=None)
    def test_friend_exist(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            friend = self.reddit.user.friends(user=self.reddit.user.me())
            assert isinstance(friend, Redditor)

    @mock.patch("time.sleep", return_value=None)
    def test_friend_not_exist(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException):
                self.reddit.user.friends(user="fake__user_user_user")

    def test_karma(self):
        self.reddit.read_only = False
        with self.use_cassette():
            karma = self.reddit.user.karma()
        assert isinstance(karma, dict)
        for subreddit in karma:
            assert isinstance(subreddit, Subreddit)
            keys = sorted(karma[subreddit].keys())
            assert ["comment_karma", "link_karma"] == keys

    def test_me(self):
        self.reddit.read_only = False
        with self.use_cassette():
            me = self.reddit.user.me()
        assert isinstance(me, Redditor)
        me.praw_is_cached = True
        assert self.reddit.user.me().praw_is_cached

    @mock.patch("time.sleep", return_value=None)
    def test_me__bypass_cache(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            me = self.reddit.user.me()
            me.praw_is_cached = True
            assert not hasattr(self.reddit.user.me(use_cache=False), "praw_is_cached")

    @mock.patch("time.sleep", return_value=None)
    def test_moderator_subreddits(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_moderator_subreddits"):
            mod_subs = list(self.reddit.user.moderator_subreddits(limit=None))
            assert mod_subs
            assert all(isinstance(x, Subreddit) for x in mod_subs)

    def test_multireddits(self):
        self.reddit.read_only = False
        with self.use_cassette():
            multireddits = self.reddit.user.multireddits()
            assert isinstance(multireddits, list)
            assert multireddits
            assert all(isinstance(x, Multireddit) for x in multireddits)

    def test_pin__without_nums(self):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission_list = []
            for i in range(1, 5):
                submission = subreddit.submit(
                    title=f"PRAW Test {i}", selftext=f"Testing .pin method {i}"
                )
                submission_list.append(submission)
                self.reddit.user.pin(submission)

            for i in range(5, 9):
                subreddit.submit(
                    title=f"PRAW Test {i}", selftext=f"Testing .pin method {i}"
                )

            new_posts = [
                submission for submission in self.reddit.user.me().new(limit=4)
            ]
            new_posts.reverse()
            assert all(map(lambda x, y: x == y, new_posts, submission_list))

    def test_pin__remove(self):
        self.reddit.read_only = False
        with self.use_cassette():
            new_posts = [
                submission for submission in self.reddit.user.me().new(limit=4)
            ]
            for post in new_posts:
                self.reddit.user.pin(post, state=False)

            new_posts = [
                submission.title for submission in self.reddit.user.me().new(limit=4)
            ]
            expected_new_posts = [f"PRAW Test {i}" for i in range(5, 9)]
            expected_new_posts.reverse()
            assert all(map(lambda x, y: x == y, new_posts, expected_new_posts))

    def test_pin__nums(self):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission_list = []
            for i in range(1, 5):
                submission = subreddit.submit(
                    title=f"PRAW Test {i}", selftext=f"Testing .pin method {i}"
                )
                submission_list.append(submission)
            submission_list.reverse()
            list(map(self.reddit.user.pin, submission_list, range(1, 5)))

            new_posts = [
                submission for submission in self.reddit.user.me().new(limit=4)
            ]
            new_posts.reverse()
            assert all(map(lambda x, y: x == y, new_posts, submission_list))

    def test_pin__empty_slot(self):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            new_posts = [
                submission for submission in self.reddit.user.me().new(limit=4)
            ]
            new_posts.reverse()
            for i in range(2, 4):
                self.reddit.user.pin(new_posts[i], state=False)
            submission = subreddit.submit(
                title="PRAW Test 5", selftext="Testing .pin method 5"
            )
            self.reddit.user.pin(submission, num=4)
            new_posts = [
                submission for submission in self.reddit.user.me().new(limit=4)
            ]
            new_posts.reverse()
            assert new_posts[-1] == submission

    def test_pin__replace_slot(self):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit(
                title="PRAW Test replace slot 1", selftext="Testing .pin method 1"
            )
            self.reddit.user.pin(submission, num=1)
            new_posts = [
                submission for submission in self.reddit.user.me().new(limit=4)
            ]
            new_posts.reverse()
            assert new_posts[-1] == submission

    def test_pin__ignore_conflicts(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.user.pin(Submission(self.reddit, "q9lvkd"), num=7)
            self.reddit.user.pin(Submission(self.reddit, "q9lvkd"), num=7)

    def test_pin__bad_request(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(prawcore.exceptions.BadRequest):
                self.reddit.user.pin(Submission(self.reddit, "i55jqj"), num=7)

    def test_pin__comment(self):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = self.reddit.comment(id="hlczc77")
            self.reddit.user.pin(comment)
            new_content = next(self.reddit.user.me().new(limit=1))
            assert not new_content == comment

    def test_subreddits(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for subreddit in self.reddit.user.subreddits():
                assert isinstance(subreddit, Subreddit)
                count += 1
            assert count > 0
