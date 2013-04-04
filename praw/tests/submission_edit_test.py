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
from requests.exceptions import HTTPError

from helper import AuthenticatedHelper


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
        submission = six_next(self.subreddit.get_top())
        if submission.distinguished:
            verify_undistinguish(submission)
            verify_distinguish(submission)
        else:
            verify_distinguish(submission)
            verify_undistinguish(submission)

    def test_edit_link(self):
        found = None
        for item in self.r.user.get_submitted():
            if not item.is_self:
                found = item
                break
        else:
            self.fail('Could not find link post')
        self.assertRaises(HTTPError, found.edit, 'text')

    def test_edit_self(self):
        found = None
        for item in self.r.user.get_submitted():
            if item.is_self:
                found = item
                break
        else:
            self.fail('Could not find self post')
        new_body = '%s\n\n+Edit Text' % found.selftext
        found = found.edit(new_body)
        self.assertEqual(found.selftext, new_body)

    def test_mark_as_nsfw(self):
        self.disable_cache()
        found = None
        for item in self.subreddit.get_top():
            if not item.over_18:
                found = item
                break
        else:
            self.fail("Couldn't find a SFW submission")
        found.mark_as_nsfw()
        found.refresh()
        self.assertTrue(found.over_18)

    def test_unmark_as_nsfw(self):
        self.disable_cache()
        found = None
        for item in self.subreddit.get_top():
            if item.over_18:
                found = item
                break
        else:
            self.fail("Couldn't find a NSFW submission")
        found.unmark_as_nsfw()
        found.refresh()
        self.assertFalse(found.over_18)
