"""Test praw.models.subreddit."""
import mock
import pytest

from ... import IntegrationTest


class TestSubreddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_submit__selftext(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubreddit.test_submit__selftext'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submission = subreddit.submit('Test Title', selftext='Test text.')
            assert submission.author == pytest.placeholders.username
            assert submission.selftext == 'Test text.'
            assert submission.title == 'Test Title'

    @mock.patch('time.sleep', return_value=None)
    def test_submit__url(self, _):
        url = 'https://praw.readthedocs.org/en/stable/'
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubreddit.test_submit__url'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submission = subreddit.submit('Test Title', url=url)
            assert submission.author == pytest.placeholders.username
            assert submission.url == url
            assert submission.title == 'Test Title'


class TestSubredditListings(IntegrationTest):
    def test_controversial(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_controversial'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_gilded'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.gilded())
        assert len(submissions) >= 50

    def test_hot(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_hot'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.hot())
        assert len(submissions) == 100

    def test_new(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_new'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.new())
        assert len(submissions) == 100

    def test_rising(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_rising'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.rising())
        assert len(submissions) == 100

    def test_top(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_top'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.top())
        assert len(submissions) == 100


class TestSubredditModeration(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_approve(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_approve'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.approve(submission)

    def test_remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_remove'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.remove(submission, spam=True)


class TestSubredditRelationships(IntegrationTest):
    REDDITOR = 'pyapitestuser3'

    @mock.patch('time.sleep', return_value=None)
    def add_remove(self, subreddit, user, relationship, _):
        relationship = getattr(subreddit, relationship)
        relationship.add(user)
        assert user in relationship
        relationship.remove(user)
        assert user not in relationship

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_banned(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__banned'):
            self.add_remove(self.subreddit, self.REDDITOR, 'banned')

    def test_contributor(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__contributor'):
            self.add_remove(self.subreddit, self.REDDITOR, 'contributor')

    @mock.patch('time.sleep', return_value=None)
    def test_moderator(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__moderator'):
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.add(self.REDDITOR)
            assert self.REDDITOR not in self.subreddit.moderator

    def test_muted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__muted'):
            self.add_remove(self.subreddit, self.REDDITOR, 'muted')

    def test_wikibanned(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__wikibanned'):
            self.add_remove(self.subreddit, self.REDDITOR, 'wikibanned')

    def test_wikicontributor(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__wikicontributor'):
            self.add_remove(self.subreddit, self.REDDITOR, 'wikicontributor')
