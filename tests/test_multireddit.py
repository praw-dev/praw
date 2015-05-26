"""Tests for Multireddit class."""

from __future__ import print_function, unicode_literals
from praw import errors
from .helper import PRAWTest, betamax


class MultiredditTest(PRAWTest):

    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)

    @betamax
    def test_add_and_remove_subreddit(self):
        multi = self.r.user.get_multireddits()[0]
        self.assertTrue(self.sr in (x['name'] for x in multi.subreddits))
        multi.remove_subreddit(self.sr)
        multi.refresh()

        self.assertFalse(self.sr in (x['name'] for x in multi.subreddits))
        multi.add_subreddit(self.sr)
        multi.refresh()
        self.assertTrue(self.sr in (x['name'] for x in multi.subreddits))

    @betamax
    def test_create_and_delete_multireddit(self):
        name = 'PRAW_{0}'.format(self.r.modhash)[:15]
        multi = self.r.create_multireddit(name)
        self.assertEqual(name.lower(), multi.name.lower())
        self.assertEqual([], multi.subreddits)

        multi.delete()
        self.assertRaises(errors.NotFound, multi.refresh)

    @betamax
    def test_get_my_multis(self):
        multi = self.r.get_my_multireddits()[0]
        self.assertEqual('publicempty', multi.display_name)
        self.assertEqual([], multi.subreddits)

    @betamax
    def test_get_multireddit(self):
        multi = self.r.user.get_multireddit('publicempty')
        self.assertEqual('/user/{0}/m/{1}'.format(self.un, 'publicempty'),
                         multi.path)

    @betamax
    def test_multireddit_get_new(self):
        multi = self.r.user.get_multireddit('publicempty')
        self.assertEqual([], list(multi.get_new()))
