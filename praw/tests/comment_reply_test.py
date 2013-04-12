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

import uuid
from six import next as six_next

from helper import configure, first, R, SR


def setup_function(function):
    configure()


def test_add_comment_and_verify():
    subreddit = R.get_subreddit(SR)
    text = 'Unique comment: %s' % uuid.uuid4()
    # pylint: disable-msg=E1101
    submission = six_next(subreddit.get_new())
    # pylint: enable-msg=E1101
    comment = submission.add_comment(text)
    assert comment.submission == submission
    assert comment.body == text


def test_add_reply_and_verify():
    subreddit = R.get_subreddit(SR)
    text = 'Unique reply: %s' % uuid.uuid4()
    found = first(subreddit.get_new(),
                  lambda submission: submission.num_comments > 0)
    assert found is not None
    comment = found.comments[0]
    reply = comment.reply(text)
    assert reply.parent_id == comment.fullname
    assert reply.body == text
