"""Test praw.models.user."""

import prawcore.exceptions
import pytest

from praw.exceptions import RedditAPIException
from praw.models import Multireddit, Redditor, Submission, Subreddit

from .. import IntegrationTest


class TestUser(IntegrationTest):
    def test_blocked(self, reddit):
        reddit.read_only = False
        blocked = reddit.user.blocked()
        assert len(blocked) > 0
        assert all(isinstance(user, Redditor) for user in blocked)

    def test_blocked_fullname(self, reddit):
        reddit.read_only = False
        blocked = next(iter(reddit.user.blocked()))
        assert blocked.fullname.startswith("t2_")
        assert not blocked.fullname.startswith("t2_t2")

    def test_contributor_subreddits(self, reddit):
        reddit.read_only = False
        count = 0
        for subreddit in reddit.user.contributor_subreddits():
            assert isinstance(subreddit, Subreddit)
            count += 1
        assert count > 0

    def test_friend_exist(self, reddit):
        reddit.read_only = False
        friend = reddit.user.friends(user=reddit.user.me())
        assert isinstance(friend, Redditor)

    def test_friend_not_exist(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException):
            reddit.user.friends(user="fake__user_user_user")

    def test_friends(self, reddit):
        reddit.read_only = False
        friends = reddit.user.friends()
        assert len(friends) > 0
        assert all(isinstance(friend, Redditor) for friend in friends)

    def test_karma(self, reddit):
        reddit.read_only = False
        karma = reddit.user.karma()
        assert isinstance(karma, dict)
        for subreddit in karma:
            assert isinstance(subreddit, Subreddit)
            keys = sorted(karma[subreddit].keys())
            assert ["comment_karma", "link_karma"] == keys

    def test_me(self, reddit):
        reddit.read_only = False
        me = reddit.user.me()
        assert isinstance(me, Redditor)
        me.praw_is_cached = True
        assert reddit.user.me().praw_is_cached

    def test_me__bypass_cache(self, reddit):
        reddit.read_only = False
        me = reddit.user.me()
        me.praw_is_cached = True
        assert not hasattr(reddit.user.me(use_cache=False), "praw_is_cached")

    @pytest.mark.cassette_name("TestUser.test_moderator_subreddits")
    def test_moderator_subreddits(self, reddit):
        reddit.read_only = False
        mod_subs = list(reddit.user.moderator_subreddits(limit=None))
        assert mod_subs
        assert all(isinstance(x, Subreddit) for x in mod_subs)

    def test_multireddits(self, reddit):
        reddit.read_only = False
        multireddits = reddit.user.multireddits()
        assert isinstance(multireddits, list)
        assert multireddits
        assert all(isinstance(x, Multireddit) for x in multireddits)

    def test_pin(self, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission_list = []
        for i in range(1, 5):
            submission = subreddit.submit(
                title=f"PRAW Test {i}", selftext=f"Testing .pin method {i}"
            )
            submission_list.append(submission)
            reddit.user.pin(submission)

        for i in range(5, 9):
            subreddit.submit(
                title=f"PRAW Test {i}", selftext=f"Testing .pin method {i}"
            )
        new_posts = list(reddit.user.me().new(limit=4))
        new_posts.reverse()
        assert new_posts == submission_list

    def test_pin__comment(self, reddit):
        reddit.read_only = False
        comment = reddit.comment("hjaga35")
        reddit.user.pin(comment)
        new_content = next(reddit.user.me().new(limit=1))
        assert new_content != comment

    def test_pin__deleted_submission(self, reddit):
        reddit.read_only = False
        with pytest.raises(prawcore.exceptions.BadRequest):
            reddit.user.pin(Submission(reddit, "qzztxz"))

    def test_pin__empty_slot(self, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        new_posts = list(reddit.user.me().new(limit=4))
        new_posts.reverse()
        for i in range(2, 4):
            reddit.user.pin(new_posts[i], state=False)
        submission = subreddit.submit(
            title="PRAW Test 5", selftext="Testing .pin method 5"
        )
        reddit.user.pin(submission, num=4)
        new_posts = list(reddit.user.me().new(limit=4))
        new_posts.reverse()
        assert new_posts[-1] == submission

    def test_pin__ignore_conflicts(self, reddit):
        reddit.read_only = False
        reddit.user.pin(Submission(reddit, "q9lvkd"))
        reddit.user.pin(Submission(reddit, "q9lvkd"))

    def test_pin__invalid_num(self, reddit):
        reddit.read_only = False
        reddit.user.pin(Submission(reddit, "qzzset"), num=7)
        submission = next(reddit.user.me().new(limit=1))
        assert submission.id == "qzzset"

    def test_pin__num(self, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission_list = []
        for i in range(1, 5):
            submission = subreddit.submit(
                title=f"PRAW Test {i}", selftext=f"Testing .pin method {i}"
            )
            submission_list.append(submission)
        submission_list.reverse()
        for num, submission in enumerate(submission_list, 1):
            reddit.user.pin(submission, num=num)

        new_posts = list(reddit.user.me().new(limit=4))
        assert new_posts == submission_list

    def test_pin__remove(self, reddit):
        reddit.read_only = False
        unpinned_posts = set()
        for post in reddit.user.me().new(limit=4):
            reddit.user.pin(post, state=False)
            unpinned_posts.add(post.title)
        new_posts = set(
            [submission.title for submission in reddit.user.me().new(limit=4)]
        )
        assert unpinned_posts != new_posts

    def test_pin__remove_num(self, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        reddit.user.pin(Submission(reddit, "qzzset"), num=1, state=False)
        submission = next(reddit.user.me().new(limit=1))
        assert submission.id != "qzzset"

    def test_pin__removed_submission(self, reddit):
        reddit.read_only = False
        with pytest.raises(prawcore.exceptions.BadRequest):
            reddit.user.pin(Submission(reddit, "qzztxz"))

    def test_pin__replace_slot(self, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit(
            title="PRAW Test replace slot 1", selftext="Testing .pin method 1"
        )
        reddit.user.pin(submission, num=1)
        new_posts = list(reddit.user.me().new(limit=4))
        new_posts.reverse()
        assert new_posts[-1] == submission

    def test_subreddits(self, reddit):
        reddit.read_only = False
        count = 0
        for subreddit in reddit.user.subreddits():
            assert isinstance(subreddit, Subreddit)
            count += 1
        assert count > 0
