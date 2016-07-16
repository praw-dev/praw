from praw.models import WikiPage
from prawcore import NotFound
import pytest

from ... import IntegrationTest


class TestWikiPage(IntegrationTest):
    def test_content_md(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        with self.recorder.use_cassette('TestWikiPage.test_attributes'):
            assert page.content_md

    def test_invalid_page(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'invalid')

        with self.recorder.use_cassette('TestWikiPage.test_invalid_page'):
            with pytest.raises(NotFound):
                page.content_md
