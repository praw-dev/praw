from unittest import mock

import pytest

from praw.models import Comment, Submission, Subreddit

from ... import IntegrationTest


class TestMultireddit(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            multi = self.reddit.user.multireddits()[0]
            multi.add("redditdev")
            assert "redditdev" in multi.subreddits

    @mock.patch("time.sleep", return_value=None)
    def test_copy(self, _):
        self.reddit.read_only = False
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            new = multi.copy()
        assert new.name == multi.name
        assert new.display_name == multi.display_name
        assert pytest.placeholders.username in new.path

    @mock.patch("time.sleep", return_value=None)
    def test_copy__with_display_name(self, _):
        self.reddit.read_only = False
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        name = "A--B\n" * 10
        with self.use_cassette():
            new = multi.copy(display_name=name)
        assert new.name == "a_b_a_b_a_b_a_b_a_b"
        assert new.display_name == name
        assert pytest.placeholders.username in new.path

    @mock.patch("time.sleep", return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            multireddit = self.reddit.multireddit.create(
                "PRAW create test", subreddits=["redditdev"]
            )
        assert multireddit.display_name == "PRAW create test"
        assert multireddit.name == "praw_create_test"

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            multi = self.reddit.user.multireddits()[0]
            multi.delete()

    @mock.patch("time.sleep", return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            multi = self.reddit.user.multireddits()[0]
            multi.remove("redditdev")
            assert "redditdev" not in multi.subreddits

    def test_subreddits(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            assert multi.subreddits
        assert all(isinstance(x, Subreddit) for x in multi.subreddits)

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        subreddits = ["pokemongo", "pokemongodev"]
        with self.use_cassette():
            multi = self.reddit.user.multireddits()[0]
            prev_path = multi.path
            multi.update(display_name="Updated display name", subreddits=subreddits)
        assert multi.display_name == "Updated display name"
        assert multi.path == prev_path
        assert multi.subreddits == subreddits


class TestMultiredditListings(IntegrationTest):
    def test_comments(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            comments = list(multi.comments())
        assert len(comments) == 100

    def test_controversial(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.gilded())
        assert len(submissions) == 100

    def test_hot(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.hot())
        assert len(submissions) == 100

    def test_new(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.new())
        assert len(submissions) == 100

    @mock.patch("time.sleep", return_value=None)
    def test_new__self_multi(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            multi = self.reddit.user.multireddits()[0]
            submissions = list(multi.new())
        assert len(submissions) == 100

    def test_random_rising(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.random_rising())
        assert len(submissions) > 0

    def test_rising(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.rising())
        assert len(submissions) > 0

    def test_top(self):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            submissions = list(multi.top())
        assert len(submissions) == 100


class TestMultiredditStreams(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_comments(self, _):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            generator = multi.stream.comments()
            for i in range(110):
                assert isinstance(next(generator), Comment)

    @mock.patch("time.sleep", return_value=None)
    def test_comments__with_pause(self, _):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            comment_stream = multi.stream.comments(pause_after=0)
            comment_count = 1
            pause_count = 1
            comment = next(comment_stream)
            while comment is not None:
                comment_count += 1
                comment = next(comment_stream)
            while comment is None:
                pause_count += 1
                comment = next(comment_stream)
            assert comment_count == 102
            assert pause_count == 4

    @mock.patch("time.sleep", return_value=None)
    def test_submissions(self, _):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette():
            generator = multi.stream.submissions()
            for i in range(102):
                assert isinstance(next(generator), Submission)

    @mock.patch("time.sleep", return_value=None)
    def test_submissions__with_pause(self, _):
        multi = self.reddit.multireddit("kjoneslol", "sfwpornnetwork")
        with self.use_cassette("TestMultiredditStreams.test_submissions"):
            generator = multi.stream.submissions(pause_after=-1)
            submission = next(generator)
            submission_count = 0
            while submission is not None:
                submission_count += 1
                submission = next(generator)
            assert submission_count == 100
