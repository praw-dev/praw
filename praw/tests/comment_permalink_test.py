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
from six import next as six_next

from helper import AuthenticatedHelper, first
from praw.objects import Comment


class CommentPermalinkTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_inbox_permalink(self):
        found = first(self.r.get_inbox(),
                      lambda item: isinstance(item, Comment))
        self.assertTrue(found is not None)
        self.assertTrue(found.id in found.permalink)

    def test_user_comments_permalink(self):
        item = six_next(self.r.user.get_comments())
        self.assertTrue(item.id in item.permalink)

    def test_get_comments_permalink(self):
        sub = self.r.get_subreddit(self.sr)
        item = six_next(sub.get_comments())
        self.assertTrue(item.id in item.permalink)
