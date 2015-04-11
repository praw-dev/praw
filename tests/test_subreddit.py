"""Tests for Subreddit class."""

from __future__ import print_function, unicode_literals

from praw import Reddit, helpers
from praw.objects import Comment, MoreComments, Submission
from .helper import PRAWTest, betamax


class ModeratorSubredditTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)

    def test_mod_mail_send(self):
        self.betamax_init()
        subject = 'Unique message: AAAA'
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        self.first(self.r.get_mod_mail(), lambda msg: msg.subject == subject)
