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

from helper import AuthenticatedHelper


class SettingsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_set_settings(self):
        title = 'Reddit API Test %s' % uuid.uuid4()
        self.subreddit.set_settings(title)
        self.assertEqual(self.subreddit.get_settings()['title'], title)

    def test_set_stylesheet(self):
        stylesheet = ('div.titlebox span.number:after {\ncontent: " %s"\n' %
                      uuid.uuid4())
        self.subreddit.set_stylesheet(stylesheet)
        self.assertEqual(stylesheet,
                         self.subreddit.get_stylesheet()['stylesheet'])

    def test_update_settings_description(self):
        self.maxDiff = None
        settings = self.subreddit.get_settings()
        settings['description'] = 'Description %s' % uuid.uuid4()
        self.subreddit.update_settings(description=settings['description'])
        new = self.subreddit.get_settings()
        # The id should change, but nothing else
        key = 'prev_description_id'
        self.assertNotEqual(settings[key], new[key])
        del settings[key]
        del new[key]
        self.assertEqual(settings, new)

    def test_update_settings_public_description(self):
        self.maxDiff = None
        settings = self.subreddit.get_settings()
        settings['public_description'] = 'Description %s' % uuid.uuid4()
        self.subreddit.update_settings(
            public_description=settings['public_description'])
        new = self.subreddit.get_settings()
        # The id should change, but nothing else
        key = 'prev_public_description_id'
        self.assertNotEqual(settings[key], new[key])
        del settings[key]
        del new[key]
        self.assertEqual(settings, new)
