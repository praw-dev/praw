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
from praw.objects import Comment


class CommentReplyNoneTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_front_page_comment_replies_are_none(self):
        # pylint: disable-msg=E1101,W0212
        item = six_next(self.r.get_all_comments())
        self.assertEqual(item._replies, None)

    def test_inbox_comment_replies_are_none(self):
        for item in self.r.get_inbox():
            if isinstance(item, Comment):
                # pylint: disable-msg=W0212
                self.assertEqual(item._replies, None)
                break
        else:
            self.fail('Could not find comment in inbox')

    def test_spambox_comments_replies_are_none(self):
        for item in self.r.get_subreddit(self.sr).get_spam():
            if isinstance(item, Comment):
                # pylint: disable-msg=W0212
                self.assertEqual(item._replies, None)
                break
        else:
            self.fail('Could not find comment in spambox')

    def test_user_comment_replies_are_none(self):
        for item in self.r.user.get_comments():
            if isinstance(item, Comment):
                # pylint: disable-msg=W0212
                self.assertEqual(item._replies, None)
                break
        else:
            self.fail('Could not find comment on other user\'s list')
