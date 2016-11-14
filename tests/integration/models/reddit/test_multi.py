from praw.models import Subreddit
import mock
import pytest

from ... import IntegrationTest


class TestMultireddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMultireddit.test_add'):
            multi = self.reddit.user.multireddits()[0]
            multi.add('redditdev')
            assert 'redditdev' in multi.subreddits

    @mock.patch('time.sleep', return_value=None)
    def test_copy(self, _):
        self.reddit.read_only = False
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultireddit.test_copy'):
            new = multi.copy()
        assert new.name == multi.name
        assert new.display_name == multi.display_name
        assert pytest.placeholders.username in new.path

    @mock.patch('time.sleep', return_value=None)
    def test_copy__with_display_name(self, _):
        self.reddit.read_only = False
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        name = 'A--B\n' * 10
        with self.recorder.use_cassette(
                'TestMultireddit.test_copy__with_display_name'):
            new = multi.copy(display_name=name)
        assert new.name == 'a_b_a_b_a_b_a_b_a_b'
        assert new.display_name == name
        assert pytest.placeholders.username in new.path

    @mock.patch('time.sleep', return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMultireddit.test_create'):
            multireddit = self.reddit.multireddit.create(
                'PRAW create test', subreddits=['redditdev'])
        assert multireddit.display_name == 'PRAW create test'
        assert multireddit.name == 'praw_create_test'

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMultireddit.test_delete'):
            multi = self.reddit.user.multireddits()[0]
            multi.delete()

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMultireddit.test_remove'):
            multi = self.reddit.user.multireddits()[0]
            multi.remove('redditdev')
            assert 'redditdev' not in multi.subreddits

    @mock.patch('time.sleep', return_value=None)
    def test_rename(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMultireddit.test_rename'):
            multi = self.reddit.user.multireddits()[0]
            multi.rename('PRAW Renamed')
            assert multi.display_name == 'PRAW Renamed'
            assert multi.name == 'praw_renamed'

    def test_subreddits(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultireddit.test_subreddits'):
            assert multi.subreddits
        assert all(isinstance(x, Subreddit) for x in multi.subreddits)

    @mock.patch('time.sleep', return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        subreddits = ['pokemongo', 'pokemongodev']
        with self.recorder.use_cassette('TestMultireddit.test_update'):
            multi = self.reddit.user.multireddits()[0]
            prev_path = multi.path
            multi.update(display_name='Updated display name',
                         subreddits=subreddits)
        assert multi.display_name == 'Updated display name'
        assert multi.path == prev_path
        assert multi.subreddits == subreddits


class TestMultiredditListings(IntegrationTest):
    def test_comments(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette(
                'TestMultiredditListings.test_comments'):
            comments = list(multi.comments())
        assert len(comments) == 100

    def test_controversial(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette(
                'TestMultiredditListings.test_controversial'):
            submissions = list(multi.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultiredditListings.test_gilded'):
            submissions = list(multi.gilded())
        assert len(submissions) == 100

    def test_hot(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultiredditListings.test_hot'):
            submissions = list(multi.hot())
        assert len(submissions) == 100

    def test_new(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultiredditListings.test_new'):
            submissions = list(multi.new())
        assert len(submissions) == 100

    @mock.patch('time.sleep', return_value=None)
    def test_new__self_multi(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestMultiredditListings.test_new__self_multi'):
            multi = self.reddit.user.multireddits()[0]
            submissions = list(multi.new())
        assert len(submissions) == 100

    def test_random_rising(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette(
                'TestMultiredditListings.test_random_rising'):
            submissions = list(multi.random_rising())
        assert len(submissions) > 0

    def test_rising(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultiredditListings.test_rising'):
            submissions = list(multi.rising())
        assert len(submissions) > 0

    def test_top(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMultiredditListings.test_top'):
            submissions = list(multi.top())
        assert len(submissions) == 100
