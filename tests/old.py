"""PRAW outdated test suite.

The tests in this file do not run on travis.ci and need to each be moved
into a respective test_NAME.py module. Individual test functions that require
network connectivity should be wrapped with a @betamax decorator.

"""

from __future__ import print_function, unicode_literals

import os
import sys
import unittest
from requests.exceptions import HTTPError
from six import text_type
from praw import errors
from .helper import AuthenticatedHelper, flair_diff


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
        # TODO: Evict submission about url
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
