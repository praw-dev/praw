"""Tests for Comment class."""

from __future__ import print_function, unicode_literals
from praw import helpers
from praw.objects import MoreComments
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


class MoreCommentsTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.submission = self.r.get_submission(url=self.more_comments_url,
                                                comment_limit=130)

    @betamax
    def test_all_comments(self):
        c_len = len(self.submission.comments)
        flat = helpers.flatten_tree(self.submission.comments)
        continue_items = [x for x in flat if isinstance(x, MoreComments) and
                          x.count == 0]
        self.assertTrue(continue_items)
        cf_len = len(flat)
        saved = self.submission.replace_more_comments(threshold=2)
        ac_len = len(self.submission.comments)
        flat = helpers.flatten_tree(self.submission.comments)
        acf_len = len(flat)
        for item in continue_items:
            self.assertTrue(item.id in [x.id for x in flat])

        self.assertEqual(len(self.submission._comments_by_id), acf_len)
        self.assertTrue(c_len < ac_len)
        self.assertTrue(c_len < cf_len)
        self.assertTrue(ac_len < acf_len)
        self.assertTrue(cf_len < acf_len)
        self.assertTrue(saved)

    @betamax
    def test_comments_method(self):
        predicate = lambda item: isinstance(item, MoreComments)
        item = self.first(self.submission.comments, predicate)
        self.assertTrue(item.comments())
