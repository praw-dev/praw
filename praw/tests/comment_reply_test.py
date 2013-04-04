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
from six import next as six_next

from helper import AuthenticatedHelper


class CommentReplyTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_comment_and_verify(self):
        text = 'Unique comment: %s' % uuid.uuid4()
        # pylint: disable-msg=E1101
        submission = six_next(self.subreddit.get_new())
        # pylint: enable-msg=E1101
        comment = submission.add_comment(text)
        self.assertEqual(comment.submission, submission)
        self.assertEqual(comment.body, text)

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        found = None
        for submission in self.subreddit.get_new():
            if submission.num_comments > 0:
                found = submission
                break
        else:
            self.fail('Could not find a submission with comments.')
        comment = found.comments[0]
        reply = comment.reply(text)
        self.assertEqual(reply.parent_id, comment.fullname)
        self.assertEqual(reply.body, text)
