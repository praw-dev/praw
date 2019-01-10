"""Test praw.models.users."""
import mock

from praw.models import Redditor, Subreddit
from .. import IntegrationTest


class TestUsers(IntegrationTest):
    def test_new(self):
        with self.recorder.use_cassette('TestUsers.test_new'):
            profiles = list(self.reddit.users.new(limit=300))
        assert len(profiles) == 300
        assert all(isinstance(profile, Subreddit) for profile in profiles)
        assert all(str(profile).startswith('u_') for profile in profiles)

    def test_popular(self):
        with self.recorder.use_cassette('TestUsers.test_popular'):
            profiles = list(self.reddit.users.popular(limit=15))
        assert len(profiles) == 15
        assert all(isinstance(profile, Subreddit) for profile in profiles)
        assert all(str(profile).startswith('u_') for profile in profiles)

    def test_search(self):
        with self.recorder.use_cassette('TestUsers.test_search'):
            found = False
            for profile in self.reddit.users.search('praw'):
                assert isinstance(profile, Redditor)
                found = True
            assert found

    @mock.patch('time.sleep', return_value=None)
    def test_stream(self, _):
        with self.recorder.use_cassette('TestUsers.test_stream'):
            generator = self.reddit.users.stream()
            for i in range(101):
                assert isinstance(next(generator), Subreddit)
