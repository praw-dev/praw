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

import unittest

from six import text_type

from helper import AuthenticatedHelper, USER_AGENT
from praw import errors, Reddit


class ModeratorUserTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        self.other = self.r.get_redditor('pyapitestuser3', fetch=True)

    def add_remove(self, add, remove, listing, add_callback=None):
        def test_add():
            add(self.other)
            if add_callback:
                add_callback()
            self.assertTrue(self.other in listing())

        def test_remove():
            remove(self.other)
            self.assertTrue(self.other not in listing())

        self.disable_cache()
        if self.other in listing():
            test_remove()
            test_add()
        else:
            test_add()
            test_remove()

    def test_accept_moderator_invite_fail(self):
        self.r.login('pyapitestuser3', '1111')
        self.assertRaises(errors.InvalidInvite,
                          self.subreddit.accept_moderator_invite)

    def test_ban(self):
        self.add_remove(self.subreddit.add_ban, self.subreddit.remove_ban,
                        self.subreddit.get_banned)

    def test_contributors(self):
        self.add_remove(self.subreddit.add_contributor,
                        self.subreddit.remove_contributor,
                        self.subreddit.get_contributors)

    def test_moderator(self):
        def add_callback():
            tmp = Reddit(USER_AGENT, disable_update_check=True)
            tmp.login('pyapitestuser3', '1111')
            tmp.get_subreddit(self.sr).accept_moderator_invite()

        self.add_remove(self.subreddit.add_moderator,
                        self.subreddit.remove_moderator,
                        self.subreddit.get_moderators,
                        add_callback)

    def test_make_moderator_by_name_failure(self):
        self.assertTrue(self.r.user in self.subreddit.get_moderators())
        self.assertRaises(errors.AlreadyModerator,
                          self.subreddit.add_moderator, text_type(self.r.user))

    def test_wiki_ban(self):
        self.add_remove(self.subreddit.add_wiki_ban,
                        self.subreddit.remove_wiki_ban,
                        self.subreddit.get_wiki_banned)

    def test_wiki_contributors(self):
        self.add_remove(self.subreddit.add_wiki_contributor,
                        self.subreddit.remove_wiki_contributor,
                        self.subreddit.get_wiki_contributors)
