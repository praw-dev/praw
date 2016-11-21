"""Test praw.models.redditor."""
from prawcore import BadRequest, Forbidden
import mock
import pytest

from ... import IntegrationTest


class TestRedditor(IntegrationTest):
    FRIEND = 'PyAPITestUser3'

    def test_friend(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestRedditor.test_friend'):
            self.reddit.redditor(self.FRIEND.lower()).friend()

    def test_friend__with_note__no_gold(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditor.test_friend__with_note__no_gold'):
            with pytest.raises(BadRequest) as excinfo:
                self.reddit.redditor(self.FRIEND.lower()).friend(note='praw')
            assert 'GOLD_REQUIRED' == excinfo.value.response.json()['reason']

    @mock.patch('time.sleep', return_value=None)
    def test_friend_info(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditor.test_friend_info'):
            redditor = self.reddit.redditor(self.FRIEND).friend_info()
            assert self.FRIEND == redditor
            assert 'date' in redditor.__dict__
            assert 'created_utc' not in redditor.__dict__
            assert hasattr(redditor, 'created_utc')

    def test_gild__no_creddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestRedditor.test_gild__no_creddits'):
            with pytest.raises(BadRequest) as excinfo:
                self.reddit.redditor('subreddit_stats').gild()
            reason = excinfo.value.response.json()['reason']
            assert 'INSUFFICIENT_CREDDITS' == reason

    @mock.patch('time.sleep', return_value=None)
    def test_message(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestRedditor.test_message'):
            redditor = self.reddit.redditor('subreddit_stats')
            redditor.message('PRAW test', 'This is a test from PRAW')

    @mock.patch('time.sleep', return_value=None)
    def test_message_from_subreddit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditor.test_message_from_subreddit'):
            redditor = self.reddit.redditor('subreddit_stats')
            redditor.message('PRAW test', 'This is a test from PRAW',
                             from_subreddit=pytest.placeholders.test_subreddit)

    def test_multireddits(self):
        redditor = self.reddit.redditor('kjoneslol')
        with self.recorder.use_cassette('TestRedditor.test_multireddits'):
            for multireddit in redditor.multireddits():
                if 'sfwpornnetwork' == multireddit.name:
                    break
            else:
                assert False, 'sfwpornnetwork not found in multireddits'

    @mock.patch('time.sleep', return_value=None)
    def test_unfriend(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestRedditor.test_unfriend'):
            redditor = self.reddit.user.friends()[0]
            assert redditor.unfriend() is None

    @mock.patch('time.sleep', return_value=None)
    def test_unblock(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestRedditor.test_unblock'):
            redditor = self.reddit.user.blocked()[0]
            redditor.unblock()


class TestRedditorListings(IntegrationTest):
    def test_comments__controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__controversial'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.controversial())
        assert len(comments) == 100

    def test_comments__hot(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__hot'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.hot())
        assert len(comments) == 100

    def test_comments__new(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__new'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.new())
        assert len(comments) == 100

    def test_comments__top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__top'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.top())
        assert len(comments) == 100

    def test_controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_controversial'):
            redditor = self.reddit.redditor('spez')
            items = list(redditor.controversial())
        assert len(items) == 100

    def test_downvoted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_downvoted'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.downvoted())
        assert len(submissions) > 0

    def test_downvoted__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_downvoted__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.downvoted())

    def test_downvoted__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_downvoted__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.downvoted())

    def test_gilded(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gilded'):
            redditor = self.reddit.redditor('spez')
            items = list(redditor.gilded(limit=50))
        assert len(items) == 50

    def test_gildings(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            items = list(redditor.gildings())
        assert isinstance(items, list)

    def test_gildings__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.gildings())

    def test_gildings__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.gildings())

    def test_hidden(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hidden'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.hidden())
        assert len(submissions) > 0

    def test_hidden__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hidden__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.hidden())

    def test_hidden__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hidden__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.hidden())

    def test_hot(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hot'):
            redditor = self.reddit.redditor('spez')
            items = list(redditor.hot())
        assert len(items) == 100

    def test_new(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_new'):
            redditor = self.reddit.redditor('spez')
            items = list(redditor.new())
        assert len(items) == 100

    def test_saved(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_saved'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            items = list(redditor.saved())
        assert len(items) > 0

    def test_saved__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_saved__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.saved())

    def test_saved__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_saved__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.saved())

    def test_submissions__controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__controversial'):
            redditor = self.reddit.redditor('spladug')
            submissions = list(redditor.submissions.controversial())
        assert len(submissions) == 100

    def test_submissions__hot(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__hot'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.submissions.hot())
        assert len(submissions) == 100

    def test_submissions__new(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__new'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.submissions.new())
        assert len(submissions) == 100

    def test_submissions__top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__top'):
            redditor = self.reddit.redditor('spladug')
            submissions = list(redditor.submissions.top())
        assert len(submissions) == 100

    def test_top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_top'):
            redditor = self.reddit.redditor('spez')
            items = list(redditor.top())
        assert len(items) == 100

    def test_upvoted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_upvoted'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.upvoted())
        assert len(submissions) > 0

    def test_upvoted__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_upvoted__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.upvoted())

    def test_upvoted__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_upvoted__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.upvoted())
