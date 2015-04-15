"""PRAW outdated test suite."""

from __future__ import print_function, unicode_literals

import os
import random
import sys
import unittest
import uuid
from requests.exceptions import HTTPError
from six import text_type
from praw import Reddit, decorators, errors, helpers
from praw.objects import Comment, Message, MoreComments
from .helper import (USER_AGENT, AuthenticatedHelper, BasicHelper, flair_diff,
                     interactive_only, local_only, prompt, reddit_only)


class OtherTests(unittest.TestCase):
    @interactive_only
    def test_get_access_information(self):
        """TODO: Remove the interactive requirement via betamax."""
        print('Visit this URL: {0}'.format(self.r.get_authorize_url('...')))
        code = prompt('Code from redir URL: ')
        token = self.r.get_access_information(code)
        expected = {'access_token': self.r.access_token,
                    'refresh_token': None,
                    'scope': set(('identity',))}
        self.assertEqual(expected, token)
        self.assertNotEqual(None, self.r.user)


class AccessControlTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_exception_get_flair_list_unauthenticated(self):
        self.assertRaises(errors.LoginOrScopeRequired, self.r.get_flair_list,
                          self.sr)

    def test_login_or_oauth_required_not_logged_in(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.add_flair_template, self.sr, 'foo')

    def test_login_or_oauth_required_not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.get_settings, self.sr)

    def test_login_required_not_logged_in(self):
        self.assertRaises(errors.LoginRequired, self.r.accept_moderator_invite,
                          self.sr)

    def test_login_required_not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginRequired, self.r.get_banned, self.sr)

    def test_oauth_scope_required(self):
        self.r.set_oauth_app_info('dummy_client', 'dummy_secret', 'dummy_url')
        self.r.set_access_credentials(set('dummy_scope',), 'dummy_token')
        self.assertRaises(errors.OAuthScopeRequired, self.r.get_me)

    def test_moderator_or_oauth_required_logged_in_from_reddit_obj(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          self.r.get_settings, self.sr)

    def test_moderator_or_oauth_required_logged_in_from_submission_obj(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        submission = self.r.get_submission(url=self.comment_url)
        self.assertRaises(errors.ModeratorOrScopeRequired, submission.remove)

    def test_moderator_or_oauth_required_logged_in_from_subreddit_obj(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        subreddit = self.r.get_subreddit(self.sr)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          subreddit.get_settings)

    def test_moderator_required_multi(self):
        self.r.login(self.un, self.un_pswd)
        sub = self.r.get_subreddit('{0}+{1}'.format(self.sr, 'test'))
        self.assertRaises(errors.ModeratorRequired, sub.get_mod_queue)

    def test_require_access_failure(self):
        self.assertRaises(TypeError, decorators.restrict_access, scope=None,
                          oauth_only=True)


class SearchTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    @reddit_only
    def test_search(self):
        self.assertTrue(len(list(self.r.search('test'))) > 2)

    @reddit_only
    def test_search_multiply_submitted_url(self):
        self.assertTrue(
            len(list(self.r.search('http://www.livememe.com/'))) > 2)

    def test_search_reddit_names(self):
        self.assertTrue(self.r.search_reddit_names('reddit'))

    @reddit_only
    def test_search_single_submitted_url(self):
        self.assertEqual(
            1, len(list(self.r.search('http://www.livememe.com/vg972qp'))))

    @reddit_only
    def test_search_with_syntax(self):
        # Searching with timestamps only possible with cloudsearch
        no_syntax = self.r.search("timestamp:1354348800..1354671600",
                                  subreddit=self.sr)
        self.assertFalse(list(no_syntax))
        with_syntax = self.r.search("timestamp:1354348800..1354671600",
                                    subreddit=self.sr, syntax='cloudsearch')
        self.assertTrue(list(with_syntax))

    @reddit_only
    def test_search_with_time_window(self):
        num = 50
        submissions = len(list(self.r.search('test', subreddit=self.sr,
                                             period='all', limit=num)))
        self.assertTrue(submissions == num)


class CacheTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_cache(self):
        subreddit = self.r.get_subreddit(self.sr)
        title = 'Test Cache: %s' % uuid.uuid4()
        body = "BODY"
        original_listing = list(subreddit.get_new(limit=5))
        subreddit.submit(title, body)
        new_listing = list(subreddit.get_new(limit=5))
        self.assertEqual(original_listing, new_listing)
        self.disable_cache()
        no_cache_listing = list(subreddit.get_new(limit=5))
        self.assertNotEqual(original_listing, no_cache_listing)

    def test_refresh_subreddit(self):
        self.disable_cache()
        subreddit = self.r.get_subreddit(self.sr)
        new_description = 'Description %s' % uuid.uuid4()
        subreddit.update_settings(public_description=new_description)
        self.assertNotEqual(new_description, subreddit.public_description)
        subreddit.refresh()
        self.assertEqual(new_description, subreddit.public_description)

    def test_refresh_submission(self):
        self.disable_cache()
        subreddit = self.r.get_subreddit(self.sr)
        submission = next(subreddit.get_top())
        same_submission = self.r.get_submission(submission_id=submission.id)
        if submission.likes:
            submission.downvote()
        else:
            submission.upvote()
        self.assertEqual(submission.likes, same_submission.likes)
        submission.refresh()
        self.assertNotEqual(submission.likes, same_submission.likes)


class EmbedTextTest(unittest.TestCase):
    embed_text = "Hello"

    def test_no_docstring(self):
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(None, self.embed_text)
        self.assertEqual(new_doc, self.embed_text)

    def test_one_liner(self):
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text("Returns something cool",
                                         self.embed_text)
        self.assertEqual(new_doc,
                         "Returns something cool\n\n" + self.embed_text)

    def test_multi_liner(self):
        doc = """Jiggers the bar

              Only run if foo is instantiated.

              """
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, doc + self.embed_text + "\n\n")

    def test_single_plus_params(self):
        doc = """Jiggers the bar

              :params foo: Self explanatory.

              """
        expected_doc = """Jiggers the bar

              {}

              :params foo: Self explanatory.

              """.format(self.embed_text)
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)

    def test_multi_plus_params(self):
        doc = """Jiggers the bar

              Jolly importment.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              """
        expected_doc = """Jiggers the bar

              Jolly importment.

              {}

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              """.format(self.embed_text)
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)

    def test_additional_params(self):
        doc = """Jiggers the bar

              Jolly important.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              The additional parameters are passed directly into
              :meth:`.get_content`. Note: the `url` parameter cannot be
              altered.

              """
        expected_doc = """Jiggers the bar

              Jolly important.

              {}

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              The additional parameters are passed directly into
              :meth:`.get_content`. Note: the `url` parameter cannot be
              altered.

              """.format(self.embed_text)
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)


class EncodingTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_author_encoding(self):
        # pylint: disable-msg=E1101
        a1 = next(self.r.get_new()).author
        a2 = self.r.get_redditor(text_type(a1))
        self.assertEqual(a1, a2)
        s1 = next(a1.get_submitted())
        s2 = next(a2.get_submitted())
        self.assertEqual(s1, s2)

    def test_unicode_comment(self):
        sub = next(self.r.get_subreddit(self.sr).get_new())
        text = 'Have some unicode: (\xd0, \xdd)'
        comment = sub.add_comment(text)
        self.assertEqual(text, comment.body)

    def test_unicode_submission(self):
        unique = uuid.uuid4()
        title = 'Wiki Entry on \xC3\x9C'
        url = 'http://en.wikipedia.org/wiki/\xC3\x9C?id=%s' % unique
        submission = self.r.submit(self.sr, title, url=url)
        self.assertTrue(title in text_type(submission))
        self.assertEqual(title, submission.title)
        self.assertEqual(url, submission.url)


class MoreCommentsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.submission = self.r.get_submission(url=self.more_comments_url,
                                                comment_limit=130)

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

        # pylint: disable-msg=W0212
        self.assertEqual(len(self.submission._comments_by_id), acf_len)
        self.assertTrue(c_len < ac_len)
        self.assertTrue(c_len < cf_len)
        self.assertTrue(ac_len < acf_len)
        self.assertTrue(cf_len < acf_len)
        self.assertTrue(saved)

    def test_comments_method(self):
        predicate = lambda item: isinstance(item, MoreComments)
        item = self.first(self.submission.comments, predicate)
        self.assertTrue(item.comments())


class SaveableTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def _helper(self, item):
        def save():
            item.save()
            item.refresh()
            self.assertTrue(item.saved)
            self.first(self.r.user.get_saved(params={'uniq': item.id}),
                       lambda x: x == item)

        def unsave():
            item.unsave()
            item.refresh()
            self.assertFalse(item.saved)

        if item.saved:
            unsave()
            save()
        else:
            save()
            unsave()

    def test_comment(self):
        self._helper(next(self.r.user.get_comments()))

    def test_submission(self):
        self._helper(next(self.r.user.get_submitted()))


class CommentEditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_reply(self):
        comment = next(self.r.user.get_comments())
        new_body = '%s\n\n+Edit Text' % comment.body
        comment = comment.edit(new_body)
        self.assertEqual(comment.body, new_body)


class CommentPermalinkTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_inbox_permalink(self):
        predicate = lambda item: isinstance(item, Comment)
        item = self.first(self.r.get_inbox(), predicate)
        self.assertTrue(item.id in item.permalink)

    def test_user_comments_permalink(self):
        item = next(self.r.user.get_comments())
        self.assertTrue(item.id in item.permalink)

    def test_get_comments_permalink(self):
        sub = self.r.get_subreddit(self.sr)
        item = next(sub.get_comments())
        self.assertTrue(item.id in item.permalink)


class CommentReplyTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_comment_and_verify(self):
        text = 'Unique comment: %s' % uuid.uuid4()
        # pylint: disable-msg=E1101
        submission = next(self.subreddit.get_new())
        # pylint: enable-msg=E1101
        comment = submission.add_comment(text)
        self.assertEqual(comment.submission, submission)
        self.assertEqual(comment.body, text)

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        predicate = lambda submission: submission.num_comments > 0
        submission = self.first(self.subreddit.get_new(), predicate)
        comment = submission.comments[0]
        reply = comment.reply(text)
        self.assertEqual(reply.parent_id, comment.fullname)
        self.assertEqual(reply.body, text)


class CommentReplyNoneTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_front_page_comment_replies_are_none(self):
        # pylint: disable-msg=E1101,W0212
        item = next(self.r.get_comments('all'))
        self.assertEqual(item._replies, None)

    def test_inbox_comment_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        comment = self.first(self.r.get_inbox(), predicate)
        # pylint: disable-msg=W0212
        self.assertEqual(comment._replies, None)

    def test_spambox_comments_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        sequence = self.r.get_subreddit(self.sr).get_spam()
        comment = self.first(sequence, predicate)
        # pylint: disable-msg=W0212
        self.assertEqual(comment._replies, None)

    def test_user_comment_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        comment = self.first(self.r.user.get_comments(), predicate)
        # pylint: disable-msg=W0212
        self.assertEqual(comment._replies, None)


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_link_flair(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = next(self.subreddit.get_new())
        self.subreddit.set_flair(sub, flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_through_submission(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = next(self.subreddit.get_new())
        sub.set_flair(flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_to_invalid_subreddit(self):
        sub = next(self.r.get_subreddit('python').get_new())
        self.assertRaises(HTTPError, self.subreddit.set_flair, sub, 'text')

    def test_add_user_flair_by_subreddit_name(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.set_flair(self.sr, self.r.user, flair_text)
        flair = self.r.get_flair(self.sr, self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], None)

    def test_add_user_flair_to_invalid_user(self):
        self.assertRaises(errors.InvalidFlairTarget, self.subreddit.set_flair,
                          self.invalid_user_name)

    def test_add_user_flair_by_name(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        flair_css = 'a%d' % random.randint(0, 1024)
        self.subreddit.set_flair(text_type(self.r.user), flair_text, flair_css)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], flair_css)

    def test_clear_user_flair(self):
        self.subreddit.set_flair(self.r.user)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair['flair_text'], None)
        self.assertEqual(flair['flair_css_class'], None)

    def test_delete_flair(self):
        flair = list(self.subreddit.get_flair_list(limit=1))[0]
        self.subreddit.delete_flair(flair['user'])
        self.assertTrue(flair not in self.subreddit.get_flair_list())

    def test_flair_csv_and_flair_list(self):
        # Clear all flair
        self.subreddit.clear_all_flair()
        self.delay(5)  # Wait for flair to clear
        self.assertEqual([], list(self.subreddit.get_flair_list()))

        # Set flair
        flair_mapping = [{'user': 'reddit', 'flair_text': 'dev'},
                         {'user': self.un, 'flair_css_class': 'xx'},
                         {'user': self.other_user_name,
                          'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.get_flair_list())))

    def test_flair_csv_many(self):
        users = ('reddit', self.un, self.other_user_name)
        flair_text_a = 'Flair: %s' % uuid.uuid4()
        flair_text_b = 'Flair: %s' % uuid.uuid4()
        flair_mapping = [{'user': 'reddit', 'flair_text': flair_text_a}] * 99
        for user in users:
            flair_mapping.append({'user': user, 'flair_text': flair_text_b})
        self.subreddit.set_flair_csv(flair_mapping)
        for user in users:
            flair = self.subreddit.get_flair(user)
            self.assertEqual(flair['flair_text'], flair_text_b)

    def test_flair_csv_optional_args(self):
        flair_mapping = [{'user': 'reddit', 'flair_text': 'reddit'},
                         {'user': self.other_user_name, 'flair_css_class':
                          'blah'}]
        self.subreddit.set_flair_csv(flair_mapping)

    def test_flair_csv_empty(self):
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, [])

    def test_flair_csv_requires_user(self):
        flair_mapping = [{'flair_text': 'hsdf'}]
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, flair_mapping)


class FlairSelectTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.priv_sr)
        self.user_flair_templates = {
            'UserCssClassOne':  ('21e00aae-09cf-11e3-a4f1-12313d281541',
                                 'default_user_flair_text_one'),
            'UserCssClassTwo':  ('2f6504c2-09cf-11e3-9d8d-12313d281541',
                                 'default_user_flair_text_two')
        }
        self.link_flair_templates = {
            'LinkCssClassOne':  ('36a573c0-09cf-11e3-b5f7-12313d096169',
                                 'default_link_flair_text_one'),
            'LinkCssClassTwo':  ('3b73f516-09cf-11e3-9a71-12313d281541',
                                 'default_link_flair_text_two')
        }

    def get_different_user_flair_class(self):
        flair = self.r.get_flair(self.subreddit, self.r.user)
        if flair == self.user_flair_templates.keys()[0]:
            different_flair = self.user_flair_templates.keys()[1]
        else:
            different_flair = self.user_flair_templates.keys()[0]
        return different_flair

    def get_different_link_flair_class(self, submission):
        flair = submission.link_flair_css_class
        if flair == self.link_flair_templates.keys()[0]:
            different_flair = self.link_flair_templates.keys()[1]
        else:
            different_flair = self.link_flair_templates.keys()[0]
        return different_flair

    def test_select_user_flair(self):
        flair_class = self.get_different_user_flair_class()
        flair_id = self.user_flair_templates[flair_class][0]
        flair_default_text = self.user_flair_templates[flair_class][1]
        self.r.select_flair(item=self.subreddit,
                            flair_template_id=flair_id)
        flair = self.r.get_flair(self.subreddit, self.r.user)
        self.assertEqual(flair['flair_text'], flair_default_text)
        self.assertEqual(flair['flair_css_class'], flair_class)

    def test_select_link_flair(self):
        sub = next(self.subreddit.get_new())
        flair_class = self.get_different_link_flair_class(sub)
        flair_id = self.link_flair_templates[flair_class][0]
        flair_default_text = self.link_flair_templates[flair_class][1]
        self.r.select_flair(item=sub,
                            flair_template_id=flair_id)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_default_text)
        self.assertEqual(sub.link_flair_css_class, flair_class)

    def test_select_user_flair_custom_text(self):
        flair_class = self.get_different_user_flair_class()
        flair_id = self.user_flair_templates[flair_class][0]
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.select_flair(item=self.subreddit,
                            flair_template_id=flair_id,
                            flair_text=flair_text)
        flair = self.r.get_flair(self.subreddit, self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], flair_class)

    def test_select_link_flair_custom_text(self):
        sub = next(self.subreddit.get_new())
        flair_class = self.get_different_link_flair_class(sub)
        flair_id = self.link_flair_templates[flair_class][0]
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.select_flair(item=sub,
                            flair_template_id=flair_id,
                            flair_text=flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)
        self.assertEqual(sub.link_flair_css_class, flair_class)

    def test_select_user_flair_remove(self):
        flair = self.r.get_flair(self.subreddit, self.r.user)
        if flair['flair_css_class'] is None:
            flair_class = self.get_different_user_flair_class()
            flair_id = self.user_flair_templates[flair_class][0]
            self.r.select_flair(item=self.subreddit,
                                flair_template_id=flair_id)
        self.r.select_flair(item=self.subreddit)
        flair = self.r.get_flair(self.subreddit, self.r.user)
        self.assertEqual(flair['flair_text'], None)
        self.assertEqual(flair['flair_css_class'], None)

    def test_select_link_flair_remove(self):
        sub = next(self.subreddit.get_new())
        if sub.link_flair_css_class is None:
            flair_class = self.get_different_link_flair_class(sub)
            flair_id = self.link_flair_templates[flair_class][0]
            self.r.select_flair(item=sub,
                                flair_template_id=flair_id)
        self.r.select_flair(item=sub)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, None)
        self.assertEqual(sub.link_flair_css_class, None)


class FlairTemplateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_user_template(self):
        self.subreddit.add_flair_template('text', 'css', True)

    def test_add_link_template(self):
        self.subreddit.add_flair_template('text', 'css', True, True)
        self.subreddit.add_flair_template(text='text', is_link=True)
        self.subreddit.add_flair_template(css_class='blah', is_link=True)
        self.subreddit.add_flair_template(is_link=True)

    def test_clear_user_templates(self):
        self.subreddit.clear_flair_templates()

    def test_clear_link_templates(self):
        self.subreddit.clear_flair_templates(True)


class ImageTests(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        test_dir = os.path.dirname(sys.modules[__name__].__file__)
        self.image_path = os.path.join(test_dir, 'files', '{0}')

    def test_delete_header(self):
        self.subreddit.delete_image(header=True)

    def test_delete_image(self):
        images = self.subreddit.get_stylesheet()['images']
        for img_data in images[:5]:
            self.subreddit.delete_image(name=img_data['name'])
        updated_images = self.subreddit.get_stylesheet()['images']
        self.assertNotEqual(images, updated_images)

    def test_delete_invalid_image(self):
        self.assertRaises(errors.BadCSSName,
                          self.subreddit.delete_image, 'invalid_image_name')

    def test_delete_invalid_params(self):
        self.assertRaises(TypeError, self.subreddit.delete_image, name='Foo',
                          header=True)

    def test_upload_invalid_file_path(self):
        self.assertRaises(IOError, self.subreddit.upload_image, 'nonexistent')

    def test_upload_uerinvalid_image(self):
        image = self.image_path.format('white-square.tiff')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    def test_upload_invalid_image_too_small(self):
        image = self.image_path.format('invalid.jpg')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    def test_upload_invalid_image_too_large(self):
        image = self.image_path.format('big')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    def test_upload_invalid_params(self):
        image = self.image_path.format('white-square.jpg')
        self.assertRaises(TypeError, self.subreddit.upload_image, image,
                          name='Foo', header=True)

    def test_upload_invalid_image_path(self):
        self.assertRaises(IOError, self.subreddit.upload_image, 'bar.png')

    @reddit_only
    def test_upload_jpg_header(self):
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    @reddit_only
    def test_upload_jpg_image(self):
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image))

    @reddit_only
    def test_upload_jpg_image_named(self):
        image = self.image_path.format('white-square.jpg')
        name = text_type(uuid.uuid4())
        self.assertTrue(self.subreddit.upload_image(image, name))
        images_json = self.subreddit.get_stylesheet()['images']
        self.assertTrue(any(name in text_type(x['name']) for x in images_json))

    @reddit_only
    def test_upload_jpg_image_no_extension(self):
        image = self.image_path.format('white-square')
        self.assertTrue(self.subreddit.upload_image(image))

    @reddit_only
    def test_upload_png_header(self):
        image = self.image_path.format('white-square.png')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    @reddit_only
    def test_upload_png_image(self):
        image = self.image_path.format('white-square.png')
        self.assertTrue(self.subreddit.upload_image(image))

    @reddit_only
    def test_upload_png_image_named(self):
        image = self.image_path.format('white-square.png')
        name = text_type(uuid.uuid4())
        self.assertTrue(self.subreddit.upload_image(image, name))
        images_json = self.subreddit.get_stylesheet()['images']
        self.assertTrue(any(name in text_type(x['name']) for x in images_json))


class LocalOnlyTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    @local_only
    def test_create_existing_redditor(self):
        self.r.login(self.un, self.un_pswd)
        self.assertRaises(errors.UsernameExists, self.r.create_redditor,
                          self.other_user_name, self.other_user_pswd)

    @local_only
    def test_create_existing_subreddit(self):
        self.r.login(self.un, self.un_pswd)
        self.assertRaises(errors.SubredditExists, self.r.create_subreddit,
                          self.sr, 'foo')

    @local_only
    def test_create_redditor(self):
        unique_name = 'PyAPITestUser%d' % random.randint(3, 10240)
        self.r.create_redditor(unique_name, '1111')

    @local_only
    def test_create_subreddit(self):
        unique_name = 'test%d' % random.randint(3, 10240)
        description = '#Welcome to %s\n\n0 item 1\n0 item 2\n' % unique_name
        self.r.login(self.un, self.un_pswd)
        self.r.create_subreddit(unique_name, 'The %s' % unique_name,
                                description)

    @local_only
    def test_delete_redditor(self):
        random_u = 'PyAPITestUser%d' % random.randint(3, 10240)
        random_p = 'pass%d' % random.randint(3, 10240)
        self.r.create_redditor(random_u, random_p)
        self.r.login(random_u, random_p)
        self.assertTrue(self.r.is_logged_in())
        self.r.delete(random_p)
        self.r.clear_authentication()
        self.assertRaises(errors.InvalidUserPass, self.r.login, random_u,
                          random_p)

    @local_only
    def test_delete_redditor_wrong_password(self):
        random_u = 'PyAPITestUser%d' % random.randint(3, 10240)
        random_p = 'pass%d' % random.randint(3, 10240)
        self.r.create_redditor(random_u, random_p)
        self.r.login(random_u, random_p)
        self.assertTrue(self.r.is_logged_in())
        self.assertRaises(errors.InvalidUserPass, self.r.delete, 'wxyz')

    @local_only
    def test_failed_feedback(self):
        self.assertRaises(errors.InvalidEmails, self.r.send_feedback,
                          'a', 'b', 'c')

    @local_only
    def test_send_feedback(self):
        msg = 'You guys are awesome. (Sent from the PRAW python module).'
        self.r.send_feedback('Bryce Boe', 'foo@foo.com', msg)


class MessageTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_get_unread_update_has_mail(self):
        self.r.send_message(self.other_user_name, 'Update has mail', 'body')
        self.r.login(self.other_user_name, self.other_user_pswd)
        self.assertTrue(self.r.user.has_mail)
        self.r.get_unread(limit=1, unset_has_mail=True, update_user=True)
        self.assertFalse(self.r.user.has_mail)

    def test_get_single_message(self):
        message1 = self.r.get_inbox(limit=1)
        message1 = list(message1)[0]
        message2 = self.r.get_message(message1.id)
        self.assertTrue(isinstance(message2, Message))
        self.assertTrue(message1 == message2)
        self.assertTrue(isinstance(message2.replies), list)
        self.assertTrue(message2.dest.lower() == self.user.name.lower())

    def test_mark_as_read(self):
        self.r.login(self.other_user_name, self.other_user_pswd)
        # pylint: disable-msg=E1101
        msg = next(self.r.get_unread(limit=1))
        msg.mark_as_read()
        self.assertTrue(msg not in self.r.get_unread(limit=5))

    def test_mark_as_unread(self):
        self.r.login(self.other_user_name, self.other_user_pswd)
        msg = self.first(self.r.get_inbox(), lambda msg: not msg.new)
        msg.mark_as_unread()
        self.assertTrue(msg in self.r.get_unread())

    def test_mark_multiple_as_read(self):
        self.r.login(self.other_user_name, self.other_user_pswd)
        messages = []
        for msg in self.r.get_unread(limit=None):
            if msg.author != self.r.user.name:
                messages.append(msg)
                if len(messages) >= 2:
                    break
        self.assertEqual(2, len(messages))
        self.r.user.mark_as_read(messages)
        unread = list(self.r.get_unread(limit=5))
        self.assertTrue(all(msg not in unread for msg in messages))

    def test_reply_to_message_and_verify(self):
        text = 'Unique message reply: %s' % uuid.uuid4()
        predicate = lambda msg: (isinstance(msg, Message)
                                 and msg.author == self.r.user)
        msg = self.first(self.r.get_inbox(), predicate)
        reply = msg.reply(text)
        self.assertEqual(reply.parent_id, msg.fullname)

    def test_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.user.send_message(subject, 'Message content')
        self.first(self.r.get_inbox(), lambda msg: msg.subject == subject)

    def test_send_from_sr(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.send_message(self.other_user_name, subject, 'Message content',
                            from_sr=self.sr)
        self.r.login(self.other_user_name, self.other_user_pswd)
        predicate = lambda msg: (msg.author is None and
                                 msg.subreddit == self.sr and
                                 msg.subject == subject)
        message = self.first(self.r.get_unread(limit=1), predicate)
        self.assertFalse(message is None)

    def test_send_invalid(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.assertRaises(errors.InvalidUser, self.r.send_message,
                          self.invalid_user_name, subject, 'Message content')


class ModeratorSubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_approve(self):
        submission = next(self.subreddit.get_spam())
        if not submission:
            self.fail('Could not find a submission to approve.')
        submission.approve()
        predicate = lambda approved: approved.id == submission.id
        self.first(self.subreddit.get_new(), predicate)

    def test_ignore_reports(self):
        submission = next(self.subreddit.get_new())
        self.assertFalse(submission in self.subreddit.get_mod_log())
        submission.ignore_reports()
        submission.report()
        self.disable_cache()
        submission.refresh()
        self.assertFalse(submission in self.subreddit.get_mod_log())
        self.assertTrue(submission.num_reports > 0)

    def test_remove(self):
        submission = next(self.subreddit.get_new())
        if not submission:
            self.fail('Could not find a submission to remove.')
        submission.remove()
        predicate = lambda removed: removed.id == submission.id
        self.first(self.subreddit.get_spam(), predicate)


class ModeratorUserTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        self.other = self.r.get_redditor(self.other_user_name, fetch=True)

    def add_remove(self, add, remove, listing, add_callback=None):
        def test_add():
            add(self.other)
            if add_callback:
                add_callback()
            self.assertTrue(self.other in listing())

        def test_remove():
            remove(self.other)
            self.assertTrue(self.other not in listing())

        self.disable_cache()
        if self.other in listing():
            test_remove()
            test_add()
        else:
            test_add()
            test_remove()

    def test_accept_moderator_invite_fail(self):
        self.r.login(self.other_user_name, self.other_user_pswd)
        self.assertRaises(errors.InvalidInvite,
                          self.subreddit.accept_moderator_invite)

    def test_ban(self):
        self.add_remove(self.subreddit.add_ban, self.subreddit.remove_ban,
                        self.subreddit.get_banned)

    def test_get_banned_note(self):
        # TODO: Update this test to add/update the ban note when ban note
        # adding is supported.
        params = {'user': self.other_non_mod_name}
        data = next(self.subreddit.get_banned(user_only=False, params=params))
        self.assertEqual(data['note'], 'no reason in particular 2')

    def test_contributors(self):
        self.add_remove(self.subreddit.add_contributor,
                        self.subreddit.remove_contributor,
                        self.subreddit.get_contributors)

    def test_moderator(self):
        def add_callback():
            tmp = Reddit(USER_AGENT, disable_update_check=True)
            tmp.login(self.other_user_name, self.other_user_pswd)
            tmp.get_subreddit(self.sr).accept_moderator_invite()

        self.add_remove(self.subreddit.add_moderator,
                        self.subreddit.remove_moderator,
                        self.subreddit.get_moderators,
                        add_callback)

    def test_make_moderator_by_name_failure(self):
        self.assertTrue(self.r.user in self.subreddit.get_moderators())
        self.assertRaises(errors.AlreadyModerator,
                          self.subreddit.add_moderator, text_type(self.r.user))

    def test_wiki_ban(self):
        self.add_remove(self.subreddit.add_wiki_ban,
                        self.subreddit.remove_wiki_ban,
                        self.subreddit.get_wiki_banned)

    def test_wiki_contributors(self):
        self.add_remove(self.subreddit.add_wiki_contributor,
                        self.subreddit.remove_wiki_contributor,
                        self.subreddit.get_wiki_contributors)


class MultiredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_get_my_multis(self):
        mymultis = self.r.get_my_multis()
        multireddit = mymultis[0]
        self.assertEqual(self.multi_name.lower(),
                         multireddit.display_name.lower())
        self.assertEqual([], multireddit.subreddits)

    def test_get_multireddit_from_user(self):
        multi = self.r.user.get_multireddit(self.multi_name)
        self.assertEqual(self.r.user.name.lower(), multi.author.name.lower())

    def test_get_new(self):
        multi = self.r.user.get_multireddit(self.multi_name)
        new = list(multi.get_new())
        self.assertEqual(0, len(new))


class SettingsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_set_settings(self):
        title = 'Reddit API Test %s' % uuid.uuid4()
        self.subreddit.set_settings(title, wikimode='anyone')
        self.assertEqual(self.subreddit.get_settings()['title'], title)

    def test_set_stylesheet(self):
        stylesheet = ('div.titlebox span.number:after {\ncontent: " %s"\n' %
                      uuid.uuid4())
        self.subreddit.set_stylesheet(stylesheet)
        self.assertEqual(stylesheet,
                         self.subreddit.get_stylesheet()['stylesheet'])
        self.r.set_stylesheet(subreddit=self.subreddit, stylesheet='')
        self.assertEqual('',
                         self.r.get_stylesheet(self.subreddit)['stylesheet'])

    def test_set_stylesheet_invalid_css(self):
        self.assertRaises(errors.BadCSS, self.subreddit.set_stylesheet,
                          'INVALID CSS')

    def test_update_settings_description(self):
        settings = self.subreddit.get_settings()
        settings['description'] = 'Description %s' % uuid.uuid4()
        self.subreddit.update_settings(description=settings['description'])
        self.assertEqual(settings, self.subreddit.get_settings())

    def test_update_settings_public_description(self):
        settings = self.subreddit.get_settings()
        settings['public_description'] = 'Description %s' % uuid.uuid4()
        self.subreddit.update_settings(
            public_description=settings['public_description'])
        self.assertEqual(settings, self.subreddit.get_settings())


class SubmissionCreateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_create_duplicate_failure(self):
        predicate = lambda item: not item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        self.assertRaises(errors.AlreadySubmitted, self.r.submit, self.sr,
                          found.title, url=found.url)

    def test_create_duplicate_success(self):
        predicate = lambda item: not item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        submission = self.r.submit(self.sr, found.title, url=found.url,
                                   resubmit=True)
        self.assertEqual(submission.title, found.title)
        self.assertEqual(submission.url, found.url)

    def test_create_link_through_subreddit(self):
        unique = uuid.uuid4()
        title = 'Test Link: %s' % unique
        url = 'http://bryceboe.com/?bleh=%s' % unique
        subreddit = self.r.get_subreddit(self.sr)
        submission = subreddit.submit(title, url=url)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.url, url)

    def test_create_self_and_verify(self):
        title = 'Test Self: %s' % uuid.uuid4()
        content = 'BODY'
        submission = self.r.submit(self.sr, title, text=content)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.selftext, content)

    def test_create_self_no_body(self):
        title = 'Test Self: %s' % uuid.uuid4()
        content = ''
        submission = self.r.submit(self.sr, title, text=content)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.selftext, content)


class SubmissionEditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_distinguish_and_undistinguish(self):
        def verify_distinguish(submission):
            submission.distinguish()
            submission.refresh()
            self.assertTrue(submission.distinguished)

        def verify_undistinguish(submission):
            submission.undistinguish()
            submission.refresh()
            self.assertFalse(submission.distinguished)

        self.disable_cache()
        sub_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=sub_id)
        if submission.distinguished:
            verify_undistinguish(submission)
            verify_distinguish(submission)
        else:
            verify_distinguish(submission)
            verify_undistinguish(submission)

    def test_edit_link(self):
        predicate = lambda item: not item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        self.assertRaises(HTTPError, found.edit, 'text')

    def test_edit_self(self):
        predicate = lambda item: item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        new_body = '%s\n\n+Edit Text' % found.selftext
        found = found.edit(new_body)
        self.assertEqual(found.selftext, new_body)

    def test_mark_as_nsfw_as_author(self):
        self.disable_cache()
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        submission = self.r.get_submission(submission_id="1nt8co")
        self.assertEqual(submission.author, self.r.user)
        originally_nsfw = submission.over_18
        if originally_nsfw:
            submission.unmark_as_nsfw()
        else:
            submission.mark_as_nsfw()
        submission.refresh()
        self.assertNotEqual(originally_nsfw, submission.over_18)

    def test_mark_as_nsfw_as_mod(self):
        self.disable_cache()
        submission = self.r.get_submission(submission_id="1nt8co")
        submission.mark_as_nsfw()
        submission.refresh()
        self.assertTrue(submission.over_18)

    def test_mark_as_nsfw_exception(self):
        self.disable_cache()
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        predicate = lambda item: item.author != self.r.user
        found = self.first(self.subreddit.get_top(), predicate)
        self.assertRaises(errors.ModeratorOrScopeRequired, found.mark_as_nsfw)

    def test_unmark_as_nsfw(self):
        self.disable_cache()
        submission = self.r.get_submission(submission_id="1nt8co")
        submission.unmark_as_nsfw()
        submission.refresh()
        self.assertFalse(submission.over_18)


class SubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_delete(self):
        submission = list(self.r.user.get_submitted())[-1]
        submission.delete()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(None, submission.author)

    def test_hide(self):
        self.disable_cache()
        predicate = lambda item: not item.hidden
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.hide()
        submission.refresh()
        self.assertTrue(submission.hidden)

    def test_report(self):
        self.disable_cache()
        # login as new user to report submission
        self.r.login(self.other_user_name, self.other_user_pswd)
        subreddit = self.r.get_subreddit(self.sr)
        predicate = lambda submission: not submission.hidden
        submission = self.first(subreddit.get_new(), predicate)
        submission.report()
        # check if submission was reported
        predicate = lambda report: report.id == submission.id
        self.first(self.r.get_subreddit(self.sr).get_reports(), predicate)

    def test_short_link(self):
        submission = next(self.r.get_new())
        if self.r.config.is_reddit:
            self.assertTrue(submission.id in submission.short_link)
        else:
            self.assertRaises(errors.ClientException, getattr, submission,
                              'short_link')

    def test_sticky_unsticky(self):
        def verify_sticky():
            submission.sticky()
            submission.refresh()
            self.assertTrue(submission.stickied)

        def verify_unsticky():
            submission.unsticky()
            submission.refresh()
            self.assertFalse(submission.stickied)

        self.disable_cache()
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)

        if submission.stickied:
            verify_unsticky()
            verify_sticky()
        else:
            verify_sticky()
            verify_unsticky()

    def test_unhide(self):
        self.disable_cache()
        predicate = lambda submission: submission.hidden
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.unhide()
        submission.refresh()
        self.assertFalse(submission.hidden)

    def test_voting(self):
        def upvote():
            submission.upvote()
            self.r.evict(submission.permalink)
            submission.refresh()
            self.assertTrue(submission.likes)

        def downvote():
            submission.downvote()
            self.r.evict(submission.permalink)
            submission.refresh()
            self.assertFalse(submission.likes)

        def clear_vote():
            submission.clear_vote()
            self.r.evict(submission.permalink)
            submission.refresh()
            self.assertEqual(submission.likes, None)

        submission = next(self.r.user.get_submitted())
        if submission.likes:
            downvote()
            upvote()
            clear_vote()
        else:
            upvote()
            downvote()
            clear_vote()
