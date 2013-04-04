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

from helper import AuthenticatedHelper
from praw import helpers
from praw.objects import MoreComments


class MoreCommentsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.submission = self.r.get_submission(url=self.more_comments_url,
                                                comment_limit=10)

    def test_all_comments(self):
        c_len = len(self.submission.comments)
        cf_len = len(helpers.flatten_tree(self.submission.comments))
        saved = self.submission.replace_more_comments(threshold=2)
        ac_len = len(self.submission.comments)
        acf_len = len(helpers.flatten_tree(self.submission.comments))

        # pylint: disable-msg=W0212
        self.assertEqual(len(self.submission._comments_by_id), acf_len)
        self.assertTrue(c_len < ac_len)
        self.assertTrue(c_len < cf_len)
        self.assertTrue(ac_len < acf_len)
        self.assertTrue(cf_len < acf_len)
        self.assertTrue(saved)

    def test_comments_method(self):
        for item in self.submission.comments:
            if isinstance(item, MoreComments):
                self.assertTrue(item.comments())
                break
        else:
            self.fail('Could not find MoreComment object.')
