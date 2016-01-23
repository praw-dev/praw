"""Tests for WikiPage class."""

from __future__ import print_function, unicode_literals
from six import text_type
from .helper import OAuthPRAWTest, PRAWTest, betamax


class WikiPageTests(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_edit_wiki_page(self):
        page = self.subreddit.get_wiki_page('index')
        content = '' if len(page.content_md) > 100 else page.content_md + 'a'
        page.edit(content)
        page.refresh()
        self.assertEqual(content, page.content_md)

    @betamax()
    def test_edit_wiki_page_settings(self):
        page = self.subreddit.get_wiki_page('index')
        current = page.get_settings()
        newperm = (current['permlevel'] + 1) % 3  # Roll to next permlevel
        newlisted = not current['listed']
        updated = page.edit_settings(permlevel=newperm, listed=newlisted)

        self.assertEqual(newperm, updated['permlevel'])
        self.assertEqual(newlisted, updated['listed'])

    @betamax()
    def test_edit_wiki_page_editors(self):
        page = self.subreddit.get_wiki_page('index')

        page.remove_editor(self.un)
        page.add_editor(self.un)

        self.r.evict(self.r.config['wiki_page_settings'].format(
                     subreddit=self.subreddit.display_name, page='index'))

        editors = page.get_settings()['editors']
        self.assertTrue(any(
            user.name.lower() == self.un.lower() for user in editors))

    @betamax()
    def test_get_wiki_page(self):
        self.assertEqual(
            '{0}:index'.format(self.sr),
            text_type(self.r.get_wiki_page(self.sr, 'index')))

    @betamax()
    def test_get_wiki_pages(self):
        result = self.subreddit.get_wiki_pages()
        self.assertTrue(result)
        tmp = self.subreddit.get_wiki_page(result[0].page).content_md
        self.assertEqual(result[0].content_md, tmp)

    @betamax()
    def test_revision_by(self):
        self.assertTrue(any(x.revision_by for x in
                            self.subreddit.get_wiki_pages()))

    @betamax()
    def test_unique_count_zero(self):
        # When `reddit_session._unique_count` = 0, WikiPages pull from cache.
        # So do Redditors and Multireddits
        page = self.r.get_wiki_page(self.sr, 'index')

        original_content = page.content_md
        content = '' if len(page.content_md) > 100 else original_content + 'a'
        page.edit(content)

        # Should not update
        self.r._unique_count = 0
        page.refresh()
        self.assertEqual(original_content, page.content_md)
        # Okay, now it will update.
        self.r._unique_count = 1
        page.refresh()
        self.assertEqual(content, page.content_md)


class OAuthWikiPageTest(OAuthPRAWTest):
    @betamax()
    def test_add_remove_wiki_ban_contributor_oauth(self):
        self.r.refresh_access_information(self.refresh_token['modwiki+contr'])
        subreddit = self.r.get_subreddit(self.sr)
        other_user = self.r.get_redditor(self.other_user_name)

        def scope_switch(method, u=0):
            # the wiki bans and contributors pages require the read scope
            self.r.refresh_access_information(self.refresh_token['read'])
            retval = list(method(params={'u': u}))
            self.r.refresh_access_information(
                self.refresh_token['modwiki+contr'])
            return retval

        subreddit.add_wiki_ban(other_user)
        self.assertTrue(other_user in scope_switch(
            subreddit.get_wiki_banned))
        subreddit.remove_wiki_ban(other_user)
        self.assertFalse(other_user in scope_switch(
            subreddit.get_wiki_banned, 1))

        subreddit.add_wiki_contributor(other_user)
        self.assertTrue(other_user in scope_switch(
            subreddit.get_wiki_contributors))
        subreddit.remove_wiki_contributor(other_user)
        self.assertFalse(other_user in scope_switch(
            subreddit.get_wiki_contributors, 1))

    @betamax()
    def test_add_remove_wiki_editor_oauth(self):
        self.r.refresh_access_information(self.refresh_token['modwiki'])
        subreddit = self.r.get_subreddit(self.sr)
        page = subreddit.get_wiki_page('index')
        other_user = self.r.get_redditor(self.other_user_name)

        page.add_editor(other_user)
        self.assertTrue(other_user in page.get_settings()['editors'])

        page.remove_editor(other_user)
        self.assertFalse(other_user in page.get_settings(
            params={'u': 1})['editors'])

    @betamax()
    def test_read_wikipage_oauth(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.r.refresh_access_information(self.refresh_token['modconfig'])
        subreddit.set_settings(subreddit.title, wikimode='modonly')

        self.r.refresh_access_information(self.refresh_token['wikiread'])
        page = subreddit.get_wiki_page('index')
        self.assertTrue(page.content_md)

        # Let's make sure we have access even when the wiki is disabled
        self.r.refresh_access_information(self.refresh_token['modconfig'])
        subreddit.set_settings(subreddit.title, wikimode='disabled')

        self.r.refresh_access_information(self.refresh_token['wikiread'])
        page = page.refresh()
        self.assertTrue(page.content_md)
