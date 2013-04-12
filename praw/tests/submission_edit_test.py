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

import pytest
from six import next as six_next
from requests.exceptions import HTTPError

from helper import configure, disable_cache, first, R, SR


SUBREDDIT = R.get_subreddit(SR)


def setup_function(function):
    configure()


def test_distinguish_and_undistinguish():
    def verify_distinguish(submission):
        submission.distinguish()
        submission.refresh()
        assert submission.distinguished

    def verify_undistinguish(submission):
        submission.undistinguish()
        submission.refresh()
        assert not submission.distinguished

    disable_cache()
    submission = six_next(SUBREDDIT.get_top())
    if submission.distinguished:
        verify_undistinguish(submission)
        verify_distinguish(submission)
    else:
        verify_distinguish(submission)
        verify_undistinguish(submission)


def test_edit_link():
    found = first(R.user.get_submitted(), lambda item: not item.is_self)
    assert found is not None
    with pytest.raises(HTTPError):
        found.edit('text')


def test_edit_self():
    found = first(R.user.get_submitted(), lambda item: item.is_self)
    assert found is not None
    new_body = '%s\n\n+Edit Text' % found.selftext
    found = found.edit(new_body)
    assert found.selftext == new_body


def test_mark_as_nsfw():
    disable_cache()
    found = first(SUBREDDIT.get_top(), lambda item: not item.over_18)
    assert found is not None
    found.mark_as_nsfw()
    found.refresh()
    assert found.over_18


def test_unmark_as_nsfw():
    disable_cache()
    found = first(SUBREDDIT.get_top(), lambda item: item.over_18)
    assert found is not None
    found.unmark_as_nsfw()
    found.refresh()
    assert not found.over_18
