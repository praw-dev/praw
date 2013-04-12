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

import pytest
import uuid

from helper import configure, first, R, SR
from praw import errors


def setup_function(function):
    configure()


def test_create_duplicate():
    found = first(R.user.get_submitted(), lambda item: not item.is_self)
    assert found is not None
    with pytest.raises(errors.AlreadySubmitted):
        R.submit(SR, found.title, url=found.url)


def test_create_link_through_subreddit():
    unique = uuid.uuid4()
    title = 'Test Link: %s' % unique
    url = 'http://bryceboe.com/?bleh=%s' % unique
    subreddit = R.get_subreddit(SR)
    submission = subreddit.submit(title, url=url)
    assert submission.title == title
    assert submission.url == url


def test_create_self_and_verify():
    title = 'Test Self: %s' % uuid.uuid4()
    content = 'BODY'
    submission = R.submit(SR, title, text=content)
    assert submission.title == title
    assert submission.selftext == content
