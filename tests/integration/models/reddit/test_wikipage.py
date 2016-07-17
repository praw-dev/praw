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


class TestWikiPageModeration(IntegrationTest):
    def test_add(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestWikiPageModeration.test_add'):
            page.mod.add('bboe')

    def test_remove(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestWikiPageModeration.test_remove'):
            page.mod.remove('bboe')

    def test_settings(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestWikiPageModeration.test_settings'):
            settings = page.mod.settings()
        assert {'editors': [], 'listed': True, 'permlevel': 0} == settings
