"""Tests for WikiPage class."""
from .helper import OAuthPRAWTest, PRAWTest, betamax


class WikiPageTests(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_revision_by(self):
        self.assertTrue(any(x.revision_by for x in
                            self.subreddit.get_wiki_pages()))


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
