"""Tests for Comment class."""

from __future__ import print_function, unicode_literals
from .helper import PRAWTest, betamax


class CommentTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax
    def test_unicode_comment(self):
        sub = next(self.subreddit.get_new())
        text = 'Have some unicode: (\xd0, \xdd)'
        comment = sub.add_comment(text)
        self.assertEqual(text, comment.body)
