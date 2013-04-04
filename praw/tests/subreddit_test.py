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
from six import text_type

from helper import AuthenticatedHelper, reddit_only


class SubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_attribute_error(self):
        self.assertRaises(AttributeError, getattr, self.subreddit, 'foo')

    def test_get_my_contributions(self):
        for subreddit in self.r.get_my_contributions():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find contributed reddit in my_contributions.')

    def test_get_my_moderation(self):
        for subreddit in self.r.get_my_moderation():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find moderated reddit in my_moderation.')

    def test_get_my_reddits(self):
        for subreddit in self.r.get_my_reddits():
            # pylint: disable-msg=W0212
            self.assertTrue(text_type(subreddit) in subreddit._info_url)

    @reddit_only
    def test_search(self):
        self.assertTrue(len(list(self.subreddit.search('test'))) > 0)

    def test_subscribe_and_verify(self):
        self.subreddit.subscribe()
        for subreddit in self.r.get_my_reddits():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find reddit in my_reddits.')

    def test_subscribe_by_name_and_verify(self):
        self.r.subscribe(self.sr)
        for subreddit in self.r.get_my_reddits():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find reddit in my_reddits.')

    def test_unsubscribe_and_verify(self):
        self.subreddit.unsubscribe()
        for subreddit in self.r.get_my_reddits():
            if text_type(subreddit) == self.sr:
                self.fail('Found reddit in my_reddits.')

    def test_unsubscribe_by_name_and_verify(self):
        self.r.unsubscribe(self.sr)
        for subreddit in self.r.get_my_reddits():
            if text_type(subreddit) == self.sr:
                self.fail('Found reddit in my_reddits.')
