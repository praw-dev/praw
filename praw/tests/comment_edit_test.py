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

from helper import AuthenticatedHelper


class CommentEditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_reply(self):
        comment = six_next(self.r.user.get_comments())
        new_body = '%s\n\n+Edit Text' % comment.body
        comment = comment.edit(new_body)
        self.assertEqual(comment.body, new_body)
