"""PRAW outdated test suite."""

from __future__ import print_function, unicode_literals

import os
import sys
import unittest
from requests.exceptions import HTTPError
from six import text_type
from praw import Reddit, decorators, errors, helpers
from praw.objects import Comment, MoreComments
from .helper import (USER_AGENT, AuthenticatedHelper, BasicHelper, flair_diff,
                     interactive_only, prompt)


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

    def test_search(self):
        self.assertTrue(len(list(self.r.search('test'))) > 2)

    def test_search_multiply_submitted_url(self):
        self.assertTrue(
            len(list(self.r.search('http://www.livememe.com/'))) > 2)

    def test_search_reddit_names(self):
        self.assertTrue(self.r.search_reddit_names('reddit'))

    def test_search_single_submitted_url(self):
        self.assertEqual(
            1, len(list(self.r.search('http://www.livememe.com/vg972qp'))))

    def test_search_with_syntax(self):
        # Searching with timestamps only possible with cloudsearch
        no_syntax = self.r.search("timestamp:1354348800..1354671600",
                                  subreddit=self.sr)
        self.assertFalse(list(no_syntax))
        with_syntax = self.r.search("timestamp:1354348800..1354671600",
                                    subreddit=self.sr, syntax='cloudsearch')
        self.assertTrue(list(with_syntax))

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
        title = 'Test Cache: %s' % self.r.modhash
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
        new_description = 'Description %s' % self.r.modhash
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
        new_doc = decorators._embed_text(None, self.embed_text)
        self.assertEqual(new_doc, self.embed_text)

    def test_one_liner(self):
        new_doc = decorators._embed_text("Returns something cool",
                                         self.embed_text)
        self.assertEqual(new_doc,
                         "Returns something cool\n\n" + self.embed_text)

    def test_multi_liner(self):
        doc = """Jiggers the bar

              Only run if foo is instantiated.

              """
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
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)


class EncodingTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_author_encoding(self):
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
        unique = self.r.modhash
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
        text = 'Unique comment: %s' % self.r.modhash
        submission = next(self.subreddit.get_new())
        comment = submission.add_comment(text)
        self.assertEqual(comment.submission, submission)
        self.assertEqual(comment.body, text)

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % self.r.modhash
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
        item = next(self.r.get_comments('all'))
        self.assertEqual(item._replies, None)

    def test_inbox_comment_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        comment = self.first(self.r.get_inbox(), predicate)
        self.assertEqual(comment._replies, None)

    def test_spambox_comments_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        sequence = self.r.get_subreddit(self.sr).get_spam()
        comment = self.first(sequence, predicate)
        self.assertEqual(comment._replies, None)

    def test_user_comment_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        comment = self.first(self.r.user.get_comments(), predicate)
        self.assertEqual(comment._replies, None)


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_link_flair(self):
        flair_text = 'Flair: %s' % self.r.modhash
        sub = next(self.subreddit.get_new())
        self.subreddit.set_flair(sub, flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_through_submission(self):
        flair_text = 'Flair: %s' % self.r.modhash
        sub = next(self.subreddit.get_new())
        sub.set_flair(flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_to_invalid_subreddit(self):
        sub = next(self.r.get_subreddit('python').get_new())
        self.assertRaises(HTTPError, self.subreddit.set_flair, sub, 'text')

    def test_add_user_flair_by_subreddit_name(self):
        flair_text = 'Flair: %s' % self.r.modhash
        self.r.set_flair(self.sr, self.r.user, flair_text)
        flair = self.r.get_flair(self.sr, self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], None)

    def test_add_user_flair_to_invalid_user(self):
        self.assertRaises(errors.InvalidFlairTarget, self.subreddit.set_flair,
                          self.invalid_user_name)

    def test_add_user_flair_by_name(self):
        flair_text = 'Flair: {0}'.format(self.r.modhash)
        flair_css = self.r.modhash
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
        flair_text_a = 'Flair: %s' % self.r.modhash
        flair_text_b = 'Flair: %s' % self.r.modhash
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
        flair_text = 'Flair: %s' % self.r.modhash
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
        flair_text = 'Flair: %s' % self.r.modhash
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

    def test_upload_jpg_header(self):
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    def test_upload_jpg_image(self):
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image))

    def test_upload_jpg_image_named(self):
        image = self.image_path.format('white-square.jpg')
        name = text_type(self.r.modhash)
        self.assertTrue(self.subreddit.upload_image(image, name))
        images_json = self.subreddit.get_stylesheet()['images']
        self.assertTrue(any(name in text_type(x['name']) for x in images_json))

    def test_upload_jpg_image_no_extension(self):
        image = self.image_path.format('white-square')
        self.assertTrue(self.subreddit.upload_image(image))

    def test_upload_png_header(self):
        image = self.image_path.format('white-square.png')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    def test_upload_png_image(self):
        image = self.image_path.format('white-square.png')
        self.assertTrue(self.subreddit.upload_image(image))

    def test_upload_png_image_named(self):
        image = self.image_path.format('white-square.png')
        name = text_type(self.r.modhash)
        self.assertTrue(self.subreddit.upload_image(image, name))
        images_json = self.subreddit.get_stylesheet()['images']
        self.assertTrue(any(name in text_type(x['name']) for x in images_json))


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
        title = 'Reddit API Test %s' % self.r.modhash
        self.subreddit.set_settings(title, wikimode='anyone')
        self.assertEqual(self.subreddit.get_settings()['title'], title)

    def test_set_stylesheet(self):
        stylesheet = ('div.titlebox span.number:after {\ncontent: " %s"\n' %
                      self.r.modhash)
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
        settings['description'] = 'Description %s' % self.r.modhash
        self.subreddit.update_settings(description=settings['description'])
        self.assertEqual(settings, self.subreddit.get_settings())

    def test_update_settings_public_description(self):
        settings = self.subreddit.get_settings()
        settings['public_description'] = 'Description %s' % self.r.modhash
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
        unique = self.r.modhash
        title = 'Test Link: %s' % unique
        url = 'http://bryceboe.com/?bleh=%s' % unique
        subreddit = self.r.get_subreddit(self.sr)
        submission = subreddit.submit(title, url=url)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.url, url)

    def test_create_self_and_verify(self):
        title = 'Test Self: %s' % self.r.modhash
        content = 'BODY'
        submission = self.r.submit(self.sr, title, text=content)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.selftext, content)

    def test_create_self_no_body(self):
        title = 'Test Self: %s' % self.r.modhash
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
