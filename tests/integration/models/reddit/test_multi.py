import pytest

from praw.models import Comment, Submission, Subreddit

from ... import IntegrationTest


class TestMultireddit(IntegrationTest):
    def test_add(self, reddit):
        reddit.read_only = False
        multi = reddit.user.multireddits()[0]
        multi.add("redditdev")
        assert "redditdev" in multi.subreddits

    def test_copy(self, reddit):
        reddit.read_only = False
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        new = multi.copy()
        assert new.name == multi.name
        assert new.display_name == multi.display_name
        assert pytest.placeholders.username in new.path

    def test_copy__with_display_name(self, reddit):
        reddit.read_only = False
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        name = "A--B\n" * 10
        new = multi.copy(display_name=name)
        assert new.name == "a_b_a_b_a_b_a_b_a_b"
        assert new.display_name == name
        assert pytest.placeholders.username in new.path

    def test_create(self, reddit):
        reddit.read_only = False
        multireddit = reddit.multireddit.create(
            display_name="PRAW create test", subreddits=["redditdev"]
        )
        assert multireddit.display_name == "PRAW create test"
        assert multireddit.name == "praw_create_test"

    def test_delete(self, reddit):
        reddit.read_only = False
        multi = reddit.user.multireddits()[0]
        multi.delete()

    def test_remove(self, reddit):
        reddit.read_only = False
        multi = reddit.user.multireddits()[0]
        multi.remove("redditdev")
        assert "redditdev" not in multi.subreddits

    def test_subreddits(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        assert multi.subreddits
        assert all(isinstance(x, Subreddit) for x in multi.subreddits)

    def test_update(self, reddit):
        reddit.read_only = False
        subreddits = ["pokemongo", "pokemongodev"]
        multi = reddit.user.multireddits()[0]
        prev_path = multi.path
        multi.update(display_name="Updated display name", subreddits=subreddits)
        assert multi.display_name == "Updated display name"
        assert multi.path == prev_path
        assert multi.subreddits == subreddits


class TestMultiredditListings(IntegrationTest):
    def test_comments(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        comments = list(multi.comments())
        assert len(comments) == 100

    def test_controversial(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.controversial())
        assert len(submissions) == 100

    def test_gilded(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.gilded())
        assert len(submissions) == 100

    def test_hot(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.hot())
        assert len(submissions) == 100

    def test_new(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.new())
        assert len(submissions) == 100

    def test_new__self_multi(self, reddit):
        reddit.read_only = False
        multi = reddit.user.multireddits()[0]
        submissions = list(multi.new())
        assert len(submissions) == 100

    def test_random_rising(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.random_rising())
        assert len(submissions) > 0

    def test_rising(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.rising())
        assert len(submissions) > 0

    def test_top(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        submissions = list(multi.top())
        assert len(submissions) == 100


class TestMultiredditStreams(IntegrationTest):
    def test_comments(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        generator = multi.stream.comments()
        for i in range(110):
            assert isinstance(next(generator), Comment)

    def test_comments__with_pause(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
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

    def test_submissions(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        generator = multi.stream.submissions()
        for i in range(102):
            assert isinstance(next(generator), Submission)

    @pytest.mark.cassette_name("TestMultiredditStreams.test_submissions")
    def test_submissions__with_pause(self, reddit):
        multi = reddit.multireddit(redditor="kjoneslol", name="sfwpornnetwork")
        generator = multi.stream.submissions(pause_after=-1)
        submission = next(generator)
        submission_count = 0
        while submission is not None:
            submission_count += 1
            submission = next(generator)
        assert submission_count == 100
