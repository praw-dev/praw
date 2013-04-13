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

import pytest
import uuid

from praw import errors
from praw.tests.helper import configure, first, R, SR, SUBREDDIT


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_create_duplicate():
    found = first(R.user.get_submitted(), lambda item: not item.is_self)
    assert found is not None
    with pytest.raises(errors.AlreadySubmitted):  # pylint: disable-msg=E1101
        R.submit(SR, found.title, url=found.url)


def test_create_link_through_subreddit():
    unique = uuid.uuid4()
    title = 'Test Link: %s' % unique
    url = 'http://bryceboe.com/?bleh=%s' % unique
    submission = SUBREDDIT.submit(title, url=url)
    assert submission.title == title
    assert submission.url == url


def test_create_self_and_verify():
    title = 'Test Self: %s' % uuid.uuid4()
    content = 'BODY'
    submission = R.submit(SR, title, text=content)
    assert submission.title == title
    assert submission.selftext == content
