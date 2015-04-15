"""Tests for AuthenticatedReddit class and its mixins."""

from __future__ import print_function, unicode_literals
from praw import errors
from .helper import PRAWTest, betamax


class AuthenticatedRedditTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)

    @betamax
    def test_create_subreddit(self):
        unique_name = 'PRAW_{0}'.format(self.r.modhash)[:15]
        self.assertRaises(errors.SubredditExists, self.r.create_subreddit,
                          self.sr, 'PRAW test_create_subreddit')
        self.r.create_subreddit(unique_name, 'The %s' % unique_name,
                                'PRAW test_create_subreddit')


class ModFlairMixinTest(AuthenticatedRedditTest):
    @betamax
    def test_get_flair_list(self):
        self.r.login(self.un, self.un_pswd)
        sub = self.r.get_subreddit(self.sr)
        self.assertTrue(next(sub.get_flair_list()))
