"""Tests for AuthenticatedReddit class and its mixins."""

from __future__ import print_function, unicode_literals
from .helper import PRAWTest, betamax


class AuthenticatedRedditTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)


class ModFlairMixinTest(AuthenticatedRedditTest):
    @betamax
    def test_get_flair_list(self):
        self.r.login(self.un, self.un_pswd)
        sub = self.r.get_subreddit(self.sr)
        self.assertTrue(next(sub.get_flair_list()))
