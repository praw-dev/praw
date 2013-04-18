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

import pytest
from six import text_type

from praw import errors, Reddit
from praw.tests.helper import (configure, disable_cache, USER_AGENT, R, SR,
                               SUBREDDIT)

OTHER = R.get_redditor('pyapitestuser3', fetch=True)


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def add_remove(add, remove, listing, add_callback=None):
    def test_add():
        add(OTHER)
        if add_callback:
            add_callback()
        assert OTHER in listing()

    def test_remove():
        remove(OTHER)
        assert OTHER not in listing()

    disable_cache()
    if OTHER in listing():
        test_remove()
        test_add()
    else:
        test_add()
        test_remove()


def test_accept_moderator_invite_fail():
    R.login('pyapitestuser3', '1111')
    with pytest.raises(errors.InvalidInvite):  # pylint: disable-msg=E1101
        SUBREDDIT.accept_moderator_invite()


def test_ban():
    add_remove(SUBREDDIT.add_ban, SUBREDDIT.remove_ban, SUBREDDIT.get_banned)


def test_contributors():
    add_remove(SUBREDDIT.add_contributor,
               SUBREDDIT.remove_contributor,
               SUBREDDIT.get_contributors)


def test_moderator():
    def add_callback():
        tmp = Reddit(USER_AGENT, disable_update_check=True)
        tmp.login('pyapitestuser3', '1111')
        tmp.get_subreddit(SR).accept_moderator_invite()

    add_remove(SUBREDDIT.add_moderator,
               SUBREDDIT.remove_moderator,
               SUBREDDIT.get_moderators,
               add_callback)


def test_make_moderator_by_name_failure():
    assert R.user in SUBREDDIT.get_moderators()
    with pytest.raises(errors.AlreadyModerator):  # pylint: disable-msg=E1101
        SUBREDDIT.add_moderator(text_type(R.user))


def test_wiki_ban():
    add_remove(SUBREDDIT.add_wiki_ban,
               SUBREDDIT.remove_wiki_ban,
               SUBREDDIT.get_wiki_banned)


def test_wiki_contributors():
    add_remove(SUBREDDIT.add_wiki_contributor,
               SUBREDDIT.remove_wiki_contributor,
               SUBREDDIT.get_wiki_contributors)
