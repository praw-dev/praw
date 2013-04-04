#!/usr/bin/env python

# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=C0103, C0302, R0903, R0904, W0201

import unittest
import uuid
import random
from six import next as six_next, text_type
from requests.exceptions import HTTPError

from helper import AuthenticatedHelper, flair_diff
from praw import errors


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_link_flair(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = six_next(self.subreddit.get_new())
        self.subreddit.set_flair(sub, flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_through_submission(self):
        flair_text = 'Falir: %s' % uuid.uuid4()
        sub = six_next(self.subreddit.get_new())
        sub.set_flair(flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_to_invalid_subreddit(self):
        sub = six_next(self.r.get_subreddit('python').get_new())
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
                         {'user': 'PyAPITestUser2', 'flair_css_class': 'xx'},
                         {'user': 'PyAPITestUser3', 'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.get_flair_list())))

    def test_flair_csv_many(self):
        users = ('reddit', 'pyapitestuser2', 'pyapitestuser3')
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
                         {'user': 'pyapitestuser3', 'flair_css_class': 'blah'}]
        self.subreddit.set_flair_csv(flair_mapping)

    def test_flair_csv_empty(self):
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, [])

    def test_flair_csv_requires_user(self):
        flair_mapping = [{'flair_text': 'hsdf'}]
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, flair_mapping)
