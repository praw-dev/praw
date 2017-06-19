from praw.models import Redditor, WikiPage
from prawcore import NotFound
import mock
import pytest

from ... import IntegrationTest


class TestWikiPage(IntegrationTest):
    def test_content_md(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        with self.recorder.use_cassette('TestWikiPage.test_content_md'):
            assert page.content_md

    def test_edit(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestWikiPage.test_edit'):
            page.edit('PRAW updated')

    def test_edit__with_reason(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestWikiPage.test_edit__with_reason'):
            page.edit('PRAW updated with reason', reason='PRAW testing')

    def test_init__with_revision(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'index',
                        revision='2f38e910-b109-11e2-ba44-12313b0d4e76')
        with self.recorder.use_cassette(
                'TestWikiPage.test_init__with_revision'):
            assert isinstance(page.revision_by, Redditor)
            assert page.revision_date == 1367295177

    def test_init__with_revision__author_deleted(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'index',
                        revision='873933a0-5550-11e2-82f1-12313b0c1e2b')
        with self.recorder.use_cassette(
                'TestWikiPage.test_init__with_revision__author_deleted'):
            assert page.revision_by is None

    def test_invalid_page(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'invalid')
        with self.recorder.use_cassette('TestWikiPage.test_invalid_page'):
            with pytest.raises(NotFound):
                page.content_md

    def test_revision_by(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        with self.recorder.use_cassette('TestWikiPage.test_revision_by'):
            assert isinstance(page.revision_by, Redditor)

    @mock.patch('time.sleep', return_value=None)
    def test_revisions(self, _):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)

        with self.recorder.use_cassette('TestWikiPage.test_revisions'):
            count = 0
            for revision in subreddit.wiki['index'].revisions(limit=None):
                count += 1
                assert isinstance(revision['author'], Redditor)
                assert isinstance(revision['page'], WikiPage)
            assert count > 0

    @mock.patch('time.sleep', return_value=None)
    def test_revisions__author_deleted(self, _):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)

        with self.recorder.use_cassette(
                'TestWikiPage.test_revisions__author_deleted'):
            revisions = subreddit.wiki['index'].revisions(limit=10)
            assert any(revision['author'] is None for revision in revisions)

    @mock.patch('time.sleep', return_value=None)
    def test_update__no_conflict(self, _):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = subreddit.wiki['praw_test_page']
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestWikiPage.test_update__no_conflict'):
            page.update(lambda x: x + ' | a suffix')

    @mock.patch('time.sleep', return_value=None)
    def test_update__conflict(self, _):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = subreddit.wiki['praw_test_page']
        repeat = [True]
        self.reddit.read_only = False

        def update_fn(text):
            if repeat[0]:
                page.edit('A new body')
                repeat[0] = False
            return text + ' | a suffix'
        with self.recorder.use_cassette('TestWikiPage.test_update__conflict'):
            page.update(update_fn)


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

    def test_update(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestWikiPageModeration.test_update'):
            updated = page.mod.update(listed=False, permlevel=1)
        assert {'editors': [], 'listed': False, 'permlevel': 1} == updated
