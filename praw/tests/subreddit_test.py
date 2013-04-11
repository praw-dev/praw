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

from helper import AuthenticatedHelper, first, reddit_only


class SubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_attribute_error(self):
        self.assertRaises(AttributeError, getattr, self.subreddit, 'foo')

    def test_get_my_contributions(self):
        found = first(self.r.get_my_contributions(),
                      lambda subreddit: text_type(subreddit) == self.sr)
        self.assertTrue(found is not None)

    def test_get_my_moderation(self):
        found = first(self.r.get_my_moderation(),
                      lambda subreddit: text_type(subreddit) == self.sr)
        self.assertTrue(found is not None)

    def test_get_my_reddits(self):
        self.assertTrue(all(text_type(subreddit) in subreddit._info_url
                            for subreddit in self.r.get_my_reddits()))

    @reddit_only
    def test_search(self):
        self.assertTrue(len(list(self.subreddit.search('test'))) > 0)

    def test_subscribe_and_verify(self):
        self.subreddit.subscribe()
        found = first(self.r.get_my_reddits(),
                      lambda subreddit: text_type(subreddit) == self.sr)
        self.assertTrue(found is not None)

    def test_subscribe_by_name_and_verify(self):
        self.r.subscribe(self.sr)
        found = first(self.r.get_my_reddits(),
                      lambda subreddit: text_type(subreddit) == self.sr)
        self.assertTrue(found is not None)

    def test_unsubscribe_and_verify(self):
        self.subreddit.unsubscribe()
        self.assertTrue(all(text_type(subreddit) != self.sr
                            for subreddit in self.r.get_my_reddits()))

    def test_unsubscribe_by_name_and_verify(self):
        self.r.unsubscribe(self.sr)
        self.assertTrue(all(text_type(subreddit) != self.sr
                            for subreddit in self.r.get_my_reddits()))
