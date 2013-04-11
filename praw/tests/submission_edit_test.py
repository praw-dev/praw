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

from helper import AuthenticatedHelper, first


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
        found = first(self.r.user.get_submitted(),
                      lambda item: not item.is_self)
        self.assertTrue(found is not None)
        self.assertRaises(HTTPError, found.edit, 'text')

    def test_edit_self(self):
        found = first(self.r.user.get_submitted(),
                      lambda item: item.is_self)
        self.assertTrue(found is not None)
        new_body = '%s\n\n+Edit Text' % found.selftext
        found = found.edit(new_body)
        self.assertEqual(found.selftext, new_body)

    def test_mark_as_nsfw(self):
        self.disable_cache()
        found = first(self.subreddit.get_top(),
                      lambda item: not item.over_18)
        self.assertTrue(found is not None)
        found.mark_as_nsfw()
        found.refresh()
        self.assertTrue(found.over_18)

    def test_unmark_as_nsfw(self):
        self.disable_cache()
        found = first(self.subreddit.get_top(),
                      lambda item: item.over_18)
        self.assertTrue(found is not None)
        found.unmark_as_nsfw()
        found.refresh()
        self.assertFalse(found.over_18)
