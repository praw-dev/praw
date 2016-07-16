"""Tests for Subreddit flair."""

from praw import errors
from .helper import PRAWTest, betamax


class FlairTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_add_user_flair__css_only(self):
        flair_css = self.r.modhash
        self.subreddit.set_flair(self.r.user, flair_css_class=flair_css)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(None, flair['flair_text'])
        self.assertEqual(flair_css, flair['flair_css_class'])

    @betamax()
    def test_add_user_flair__text_and_css(self):
        flair_text = 'Text & CSS: {0}'.format(self.r.modhash)
        flair_css = self.r.modhash
        self.subreddit.set_flair(self.r.user, flair_text, flair_css)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair_text, flair['flair_text'])
        self.assertEqual(flair_css, flair['flair_css_class'])

    @betamax()
    def test_add_user_flair__text_only(self):
        flair_text = 'Text Only: {0}'.format(self.r.modhash)
        self.subreddit.set_flair(self.r.user, flair_text)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair_text, flair['flair_text'])
        self.assertEqual(None, flair['flair_css_class'])

    @betamax()
    def test_add_user_flair_to_invalid_user(self):
        self.assertRaises(errors.InvalidFlairTarget, self.subreddit.set_flair,
                          self.invalid_user_name)

    @betamax()
    def test_clear_user_flair(self):
        self.subreddit.set_flair(self.r.user)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(None, flair['flair_text'])
        self.assertEqual(None, flair['flair_css_class'])

    @betamax()
    def test_delete_flair(self):
        flair = next(self.subreddit.get_flair_list(limit=1))
        self.subreddit.delete_flair(flair['user'])
        self.assertTrue(flair not in self.subreddit.get_flair_list())
