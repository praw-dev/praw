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

from helper import configure, first, MORE_COMMENTS_URL, R
from praw import helpers
from praw.objects import MoreComments


def setup_function(function):
    configure()


def test_all_comments():
    submission = R.get_submission(url=MORE_COMMENTS_URL, comment_limit=10)
    c_len = len(submission.comments)
    cf_len = len(helpers.flatten_tree(submission.comments))
    saved = submission.replace_more_comments(threshold=2)
    ac_len = len(submission.comments)
    acf_len = len(helpers.flatten_tree(submission.comments))

    # pylint: disable-msg=W0212
    assert len(submission._comments_by_id) == acf_len
    assert c_len < ac_len
    assert c_len < cf_len
    assert ac_len < acf_len
    assert cf_len < acf_len
    assert saved


def test_comments_method():
    submission = R.get_submission(url=MORE_COMMENTS_URL, comment_limit=10)
    found = first(submission.comments,
                  lambda item: isinstance(item, MoreComments))
    assert found is not None
    assert found.comments()
