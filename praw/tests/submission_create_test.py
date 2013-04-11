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

from helper import AuthenticatedHelper, first
from praw import errors


class SubmissionCreateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_create_duplicate(self):
        found = first(self.r.user.get_submitted(),
                      lambda item: not item.is_self)
        self.assertTrue(found is not None)
        self.assertRaises(errors.AlreadySubmitted, self.r.submit, self.sr,
                          found.title, url=found.url)

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
