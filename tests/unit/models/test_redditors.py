"""Test praw.models.redditors."""

from .. import UnitTest


class TestRedditors(UnitTest):
    def test_search__params_not_modified(self):
        params = {'dummy': 'value'}
        generator = self.reddit.redditors.search(None, params=params)
        assert generator.params['dummy'] == 'value'
        assert params == {'dummy': 'value'}
