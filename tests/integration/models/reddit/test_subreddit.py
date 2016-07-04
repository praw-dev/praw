"""Test praw.models.subreddit."""
from praw.models import Comment, Redditor
import mock
import pytest

from ... import IntegrationTest


class TestSubreddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_message(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_message'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            subreddit.message('Test from PRAW', message='Test content')

    @mock.patch('time.sleep', return_value=None)
    def test_submit__selftext(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_submit__selftext'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submission = subreddit.submit('Test Title', selftext='Test text.')
            assert submission.author == self.reddit.config.username
            assert submission.selftext == 'Test text.'
            assert submission.title == 'Test Title'

    @mock.patch('time.sleep', return_value=None)
    def test_submit__url(self, _):
        url = 'https://praw.readthedocs.org/en/stable/'
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_submit__url'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submission = subreddit.submit('Test Title', url=url)
            assert submission.author == self.reddit.config.username
            assert submission.url == url
            assert submission.title == 'Test Title'


class TestSubredditFlair(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__iter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test__iter'):
            mapping = list(self.subreddit.flair)
            assert len(mapping) > 0
            assert all(isinstance(x['user'], Redditor) for x in mapping)

    @mock.patch('time.sleep', return_value=None)
    def test_delete_all(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test_delete_all'):
            response = self.subreddit.flair.delete_all()
            # Betamax only saves one of the POST requests to flaircsv because
            # the default matcher only matches on URI and method. Matching with
            # the body included records all the requests, but then does not
            # match when replaying requests.
            assert len(response) > 0
            assert all('removed' in x['status'] for x in response)

    def test_set__redditor(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__redditor'):
            redditor = self.subreddit._reddit.redditor(
                self.reddit.config.username)
            self.subreddit.flair.set(redditor, 'redditor flair')

    def test_set__redditor_string(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__redditor_string'):
            self.subreddit.flair.set(self.reddit.config.username, 'new flair',
                                     'some class')

    def test_set__submission(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__submission'):
            submission = self.subreddit._reddit.submission('4b536p')
            self.subreddit.flair.set(submission, 'submission flair')

    def test_update(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test_update'):
            redditor = self.subreddit._reddit.redditor(
                self.reddit.config.username)

            flair_list = [redditor, 'spez', {'user': 'bsimpson'},
                          {'user': 'spladug', 'flair_text': '',
                           'flair_css_class': ''}]
            response = self.subreddit.flair.update(flair_list,
                                                   css_class='default')
            assert all(x['ok'] for x in response)
            assert not any(x['errors'] for x in response)
            assert not any(x['warnings'] for x in response)
            assert len([x for x in response if 'added' in x['status']]) == 3
            assert len([x for x in response if 'removed' in x['status']]) == 1
            for i, name in enumerate([str(redditor), 'spez', 'bsimpson',
                                      'spladug']):
                assert name in response[i]['status']


class TestSubredditListings(IntegrationTest):
    def test_comments(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_comments'):
            subreddit = self.reddit.subreddit('askreddit')
            comments = list(subreddit.comments())
        assert len(comments) == 100

    def test_controversial(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_controversial'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        with self.recorder.use_cassette('TestSubredditListings.test_gilded'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.gilded())
        assert len(submissions) >= 50

    def test_hot(self):
        with self.recorder.use_cassette('TestSubredditListings.test_hot'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.hot())
        assert len(submissions) == 100

    def test_new(self):
        with self.recorder.use_cassette('TestSubredditListings.test_new'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.new())
        assert len(submissions) == 100

    def test_rising(self):
        with self.recorder.use_cassette('TestSubredditListings.test_rising'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.rising())
        assert len(submissions) == 100

    def test_top(self):
        with self.recorder.use_cassette('TestSubredditListings.test_top'):
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

    def test_distinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_distinguish'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.distinguish(submission)

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_ignore_reports'):
            submission = self.reddit.submission('31ybt2')
            self.subreddit.mod.ignore_reports(submission)

    def test_remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_remove'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.remove(submission, spam=True)

    def test_undistinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_undistinguish'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.undistinguish(submission)

    def test_unignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_unignore_reports'):
            submission = self.reddit.submission('31ybt2')
            self.subreddit.mod.unignore_reports(submission)


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
        with self.recorder.use_cassette('TestSubredditRelationships__banned'):
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
        with self.recorder.use_cassette('TestSubredditRelationships__muted'):
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


class TestSubredditStreams(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_comments(self):
        with self.recorder.use_cassette(
                'TestSubredditStreams__comments'):
            generator = self.subreddit.stream.comments()
            for i in range(101):
                assert isinstance(next(generator), Comment)
