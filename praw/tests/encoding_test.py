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

from __future__ import unicode_literals

import uuid
from six import next as six_next, text_type

from helper import configure, R, SR


def setup_function(function):
    configure()


def test_author_encoding():
    # pylint: disable-msg=E1101
    a1 = six_next(R.get_new()).author
    a2 = R.get_redditor(text_type(a1))
    assert a1 == a2
    s1 = six_next(a1.get_submitted())
    s2 = six_next(a2.get_submitted())
    assert s1 == s2


def test_unicode_comment():
    sub = six_next(R.get_subreddit(SR).get_new())
    text = 'Have some unicode: (\xd0, \xdd)'
    comment = sub.add_comment(text)
    assert text == comment.body


def test_unicode_submission():
    unique = uuid.uuid4()
    title = 'Wiki Entry on \xC3\x9C'
    url = 'http://en.wikipedia.org/wiki/\xC3\x9C?id=%s' % unique
    submission = R.submit(SR, title, url=url)
    str(submission)
    assert title == submission.title
    assert url == submission.url
