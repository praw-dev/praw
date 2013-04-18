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

from six import next as six_next

from praw.objects import LoggedInRedditor
from praw.tests.helper import (configure, delay, OTHER_USER_ID,
                               OTHER_USER_NAME, R)


OTHER_USER = R.get_redditor(OTHER_USER_NAME)


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_add_remove_friends():
    def verify_add():
        OTHER_USER.friend()
        assert OTHER_USER in R.user.get_friends()

    def verify_remove():
        OTHER_USER.unfriend()
        assert OTHER_USER not in R.user.get_friends()

    if OTHER_USER in R.user.get_friends():
        verify_remove()
        verify_add()
    else:
        verify_add()
        verify_remove()


def test_duplicate_login():
    R.login(OTHER_USER_NAME, '1111')


def test_get_disliked():
    # Pulls from get_liked. Problem here may come from get_liked
    item = six_next(R.user.get_liked())
    item.downvote()
    delay()  # The queue needs to be processed
    assert item not in list(R.user.get_liked())


def test_get_hidden():
    submission = six_next(R.user.get_submitted())
    submission.hide()
    delay()  # The queue needs to be processed
    item = six_next(R.user.get_hidden())
    item.unhide()
    delay()
    assert item not in list(R.user.get_hidden())


def test_get_liked():
    # Pulls from get_disliked. Problem here may come from get_disliked
    item = six_next(R.user.get_disliked())
    item.upvote()
    delay()  # The queue needs to be processed
    assert item not in list(R.user.get_disliked())


def test_get_redditor():
    assert OTHER_USER_ID == OTHER_USER.id


def test_user_set_on_login():
    assert isinstance(R.user, LoggedInRedditor)
