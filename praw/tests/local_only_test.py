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
import random

from helper import BasicHelper, local_only
from praw import errors


class LocalOnlyTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    @local_only
    def test_create_existing_redditor(self):
        self.r.login(self.un, '1111')
        self.assertRaises(errors.UsernameExists, self.r.create_redditor,
                          self.other_user_name, '1111')

    @local_only
    def test_create_existing_subreddit(self):
        self.r.login(self.un, '1111')
        self.assertRaises(errors.SubredditExists, self.r.create_subreddit,
                          self.sr, 'foo')

    @local_only
    def test_create_redditor(self):
        unique_name = 'PyAPITestUser%d' % random.randint(3, 10240)
        self.r.create_redditor(unique_name, '1111')

    @local_only
    def test_create_subreddit(self):
        unique_name = 'test%d' % random.randint(3, 10240)
        description = '#Welcome to %s\n\n0 item 1\n0 item 2\n' % unique_name
        self.r.login(self.un, '1111')
        self.r.create_subreddit(unique_name, 'The %s' % unique_name,
                                description)

    @local_only
    def test_failed_feedback(self):
        self.assertRaises(errors.InvalidEmails, self.r.send_feedback,
                          'a', 'b', 'c')

    @local_only
    def test_send_feedback(self):
        msg = 'You guys are awesome. (Sent from the PRAW python module).'
        self.r.send_feedback('Bryce Boe', 'foo@foo.com', msg)
