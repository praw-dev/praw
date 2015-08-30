"""Tests for Comment class."""

from __future__ import print_function, unicode_literals
import pickle
import mock
from praw import errors, helpers
from praw.objects import Comment, MoreComments
from .helper import OAuthPRAWTest, PRAWTest, betamax


class CommentTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_add_comment(self):
        text = 'Unique comment: {0}'.format(self.r.modhash)
        submission = next(self.subreddit.get_new())
        comment = submission.add_comment(text)
        self.assertEqual(comment.get_tree(), submission)
        self.assertEqual(comment.get_submission(), submission)
        self.assertEqual(comment.get_parent(), submission)
        self.assertEqual(comment.get_context(), submission)
        self.assertRaises(TypeError, comment.get_context, context_number="5")
        self.assertEqual(comment.body, text)
        # Remove next line after PRAW 4
        self.assertEqual(comment.submission, submission)

    @betamax()
    def test_add_reply(self):
        text = 'Unique reply: {0}'.format(self.r.modhash)
        submission = self.first(self.subreddit.get_new(),
                                lambda submission: submission.num_comments > 0)
        comment = submission.comments[0]
        reply = comment.reply(text)
        self.assertEqual(reply.parent_id, comment.fullname)
        self.assertEqual(reply.body, text)
        self.assertEqual(reply.get_parent(), submission)

    @betamax()
    def test_edit(self):
        comment = next(self.r.user.get_comments())
        new_body = '{0}\n\n+Edit Text'.format(comment.body)
        comment = comment.edit(new_body)
        self.assertEqual(comment.body, new_body)

    @betamax()
    def test_front_page_comment_replies_are_none(self):
        item = next(self.r.get_comments('all'))
        self.assertEqual(item._replies, None)

    @betamax()
    def test_get_comments_context_link(self):
        item = next(self.subreddit.get_comments())
        self.assertTrue(item.id in item.default_contextlink)
        self.assertTrue(item.id in item.contextlink(5))
        self.assertTrue(item.id in item._fast_default_contextlink)

        self.assertRaises(TypeError, item.contextlink, context_number="5")

    @betamax()
    def test_get_comments_parentlink(self):
        item = next(self.subreddit.get_comments())
        self.assertTrue(item.sid in item.parentlink)
        self.assertTrue(item.sid in item._fast_parentlink)

    @betamax()
    def test_get_comments_permalink(self):
        item = next(self.subreddit.get_comments())
        self.assertTrue(item.id in item.permalink)
        self.assertTrue(item.id in item._fast_permalink)

    @betamax()
    def test_inbox_comment_context_link(self):
        item = self.first(self.r.get_inbox(),
                          lambda item: isinstance(item, Comment))
        self.assertTrue(item.id in item.default_contextlink)
        self.assertTrue(item.id in item.contextlink(5))
        self.assertTrue(item.id in item._fast_default_contextlink)

        self.assertRaises(TypeError, item.contextlink, context_number="5")

    @betamax()
    def test_inbox_comment_parentlink(self):
        item = self.first(self.r.get_inbox(),
                          lambda item: isinstance(item, Comment))
        self.assertTrue(item.sid in item.parentlink)
        self.assertTrue(item.sid in item._fast_parentlink)

    @betamax()
    def test_inbox_comment_permalink(self):
        item = self.first(self.r.get_inbox(),
                          lambda item: isinstance(item, Comment))
        self.assertTrue(item.id in item.permalink)
        self.assertTrue(item.id in item._fast_permalink)

    @betamax()
    def test_inbox_comment_replies_are_none(self):
        comment = self.first(self.r.get_inbox(),
                             lambda item: isinstance(item, Comment))
        self.assertEqual(comment._replies, None)

    @betamax()
    def test_save_comment(self):
        comment = next(self.r.user.get_comments())

        comment.save()
        comment.refresh()
        self.assertTrue(comment.saved)
        self.first(self.r.user.get_saved(), lambda x: x == comment)

        comment.unsave()
        comment.refresh()
        self.assertFalse(comment.saved)
        self.assertFalse(comment in self.r.user.get_saved(params={'u': 1}))

    @betamax()
    def test_spambox_comments_replies_are_none(self):
        sequence = self.r.get_subreddit(self.sr).get_spam()
        comment = self.first(sequence,
                             lambda item: isinstance(item, Comment))
        self.assertEqual(comment._replies, None)

    @betamax()
    def test_unicode_comment(self):
        sub = next(self.subreddit.get_new())
        text = 'Have some unicode: (\xd0, \xdd)'
        comment = sub.add_comment(text)
        self.assertEqual(text, comment.body)

    @betamax()
    def test_user_comment_contextlink(self):
        item = next(self.r.user.get_comments())
        self.assertTrue(item.id in item.default_contextlink)
        self.assertTrue(item.id in item.contextlink(5))
        self.assertTrue(item.id in item._fast_default_contextlink)

    @betamax()
    def test_user_comment_parentlink(self):
        item = next(self.r.user.get_comments())
        self.assertTrue(item.sid in item.parentlink)
        self.assertTrue(item.sid in item._fast_parentlink)

    @betamax()
    def test_user_comment_permalink(self):
        item = next(self.r.user.get_comments())
        self.assertTrue(item.id in item.permalink)
        self.assertTrue(item.id in item._fast_permalink)

    @betamax()
    def test_user_comment_replies_are_none(self):
        comment = self.first(self.r.user.get_comments(),
                             lambda item: isinstance(item, Comment))
        self.assertEqual(comment._replies, None)

    def _test_pickling(self, protocol):
        comment = next(self.r.user.get_comments())
        with mock.patch('praw.BaseReddit.request_json') as request_json_func:
            unpickled_comment = pickle.loads(pickle.dumps(comment, protocol))
            self.assertEqual(comment, unpickled_comment)
            self.assertEqual(request_json_func.called, 0)

    @betamax()
    def test_pickling_v0(self):
        self._test_pickling(0)

    @betamax()
    def test_pickling_v1(self):
        self._test_pickling(1)

    @betamax()
    def test_pickling_v2(self):
        self._test_pickling(2)


class MoreCommentsTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.submission = self.r.get_submission(url=self.more_comments_url,
                                                comment_limit=130)

    @betamax()
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

    @betamax()
    def test_comments_method(self):
        item = self.first(self.submission.comments,
                          lambda item: isinstance(item, MoreComments))
        self.assertTrue(item.comments())


class OAuthCommentTest(OAuthPRAWTest):
    @betamax()
    def test_raise_invalidcomment_oauth(self):
        fullname = '{0}_{1}'.format(self.r.config.by_object[Comment],
                                    self.comment_deleted_id)
        self.r.refresh_access_information(self.refresh_token['submit'])
        comment = self.r.get_info(thing_id=fullname)
        self.assertRaises(errors.InvalidComment, comment.reply, 'test')
        invalid_comment = errors.InvalidComment()
        self.assertEqual(invalid_comment.ERROR_TYPE, str(invalid_comment))
