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

from __future__ import unicode_literals

import uuid
from six import next as six_next, text_type

from praw.tests.helper import configure, R, SR, SUBREDDIT


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_author_encoding():
    # pylint: disable-msg=E1101
    author1 = six_next(R.get_new()).author
    author2 = R.get_redditor(text_type(author1))
    assert author1 == author2
    subreddit1 = six_next(author1.get_submitted())
    subreddit2 = six_next(author2.get_submitted())
    assert subreddit1 == subreddit2


def test_unicode_comment():
    sub = six_next(SUBREDDIT.get_new())
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
