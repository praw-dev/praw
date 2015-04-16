"""Tests for WikiPage class."""

from __future__ import print_function, unicode_literals
from six import text_type
from .helper import PRAWTest, betamax


class WikiPageTests(PRAWTest):
    def betamax_init(self):
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax
    def test_edit_wiki_page(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        page = self.subreddit.get_wiki_page('index')
        content = '' if len(page.content_md) > 100 else page.content_md + 'a'
        page.edit(content)
        self.assertEqual(
            content, self.subreddit.get_wiki_page('index', u=1).content_md)

    @betamax
    def test_get_wiki_page(self):
        self.assertEqual(
            '{0}:index'.format(self.sr),
            text_type(self.r.get_wiki_page(self.sr, 'index')))

    @betamax
    def test_get_wiki_pages(self):
        result = self.subreddit.get_wiki_pages()
        self.assertTrue(result)
        tmp = self.subreddit.get_wiki_page(result[0].page).content_md
        self.assertEqual(result[0].content_md, tmp)

    @betamax
    def test_revision_by(self):
        self.assertTrue(any(x.revision_by for x in
                            self.subreddit.get_wiki_pages()))
