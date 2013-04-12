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

from six import next as six_next

from helper import configure, first, R, SR
from praw.objects import Comment


def setup_function(function):
    configure()


def test_front_page_comment_replies_are_none():
    # pylint: disable-msg=E1101,W0212
    item = six_next(R.get_all_comments())
    assert item._replies is None


def test_inbox_comment_replies_are_none():
    found = first(R.get_inbox(), lambda item: isinstance(item, Comment))
    assert found is not None
    assert found._replies is None


def test_spambox_comments_replies_are_none():
    found = first(R.get_subreddit(SR).get_spam(),
                  lambda item: isinstance(item, Comment))
    assert found is not None
    assert found._replies is None


def test_user_comment_replies_are_none():
    found = first(R.user.get_comments(),
                  lambda item: isinstance(item, Comment))
    assert found is not None
    assert found._replies is None
