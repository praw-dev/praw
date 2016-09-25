"""Test praw.models.front."""
from .. import UnitTest


class TestSubreddits(UnitTest):
    def test_search__params_not_modified(self):
        params = {'dummy': 'value'}
        generator = self.reddit.subreddits.search(None, params=params)
        assert generator.params['dummy'] == 'value'
        assert params == {'dummy': 'value'}
