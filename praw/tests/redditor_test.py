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

from helper import AuthenticatedHelper
from praw.objects import LoggedInRedditor


class RedditorTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.other_user = self.r.get_redditor(self.other_user_name)

    def test_add_remove_friends(self):
        def verify_add():
            self.other_user.friend()
            self.assertTrue(self.other_user in self.r.user.get_friends())

        def verify_remove():
            self.other_user.unfriend()
            self.assertTrue(self.other_user not in self.r.user.get_friends())

        if self.other_user in self.r.user.get_friends():
            verify_remove()
            verify_add()
        else:
            verify_add()
            verify_remove()

    def test_duplicate_login(self):
        self.r.login(self.other_user_name, '1111')

    def test_get_disliked(self):
        # Pulls from get_liked. Problem here may come from get_liked
        item = six_next(self.r.user.get_liked())
        item.downvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_liked()))

    def test_get_hidden(self):
        submission = six_next(self.r.user.get_submitted())
        submission.hide()
        self.delay()  # The queue needs to be processed
        item = six_next(self.r.user.get_hidden())
        item.unhide()
        self.delay()
        self.assertFalse(item in list(self.r.user.get_hidden()))

    def test_get_liked(self):
        # Pulls from get_disliked. Problem here may come from get_disliked
        item = six_next(self.r.user.get_disliked())
        item.upvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_disliked()))

    def test_get_redditor(self):
        self.assertEqual(self.other_user_id, self.other_user.id)

    def test_user_set_on_login(self):
        self.assertTrue(isinstance(self.r.user, LoggedInRedditor))
