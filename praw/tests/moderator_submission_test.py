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


class ModeratorSubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_approve(self):
        submission = six_next(self.subreddit.get_spam())
        if not submission:
            self.fail('Could not find a submission to approve.')
        submission.approve()
        found = first(self.subreddit.get_new(),
                      lambda approved: approved.id == submission.id)
        self.assertTrue(found is not None)

    def test_remove(self):
        submission = six_next(self.subreddit.get_new())
        if not submission:
            self.fail('Could not find a submission to remove.')
        submission.remove()
        found = first(self.subreddit.get_spam(),
                      lambda removed: removed.id == submission.id)
        self.assertTrue(found is not None)
