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

from helper import BasicHelper, USER_AGENT
from praw import decorators, errors, Reddit


class AccessControlTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_exception_get_flair_list_authenticated(self):
        self.r.login(self.un, '1111')
        self.assertTrue(self.r.get_flair_list(self.sr))

    def test_exception_get_flair_list_unauthenticated(self):
        self.assertTrue(self.r.get_flair_list(self.sr))

    def test_login_or_oauth_required_not_logged_in(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.add_flair_template, self.sr, 'foo')

    def test_login_or_oauth_required_not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.get_settings, self.sr)

    def test_login_required_not_logged_in(self):
        self.assertRaises(errors.LoginRequired, self.r.accept_moderator_invite,
                          self.sr)

    def test_login_required_not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginRequired, self.r.get_banned, self.sr)

    def test_oauth_scope_required(self):
        self.r.set_oauth_app_info('dummy_client', 'dummy_secret', 'dummy_url')
        self.r.set_access_credentials(set('dummy_scope',), 'dummy_token')
        self.assertRaises(errors.OAuthScopeRequired, self.r.get_me)

    def test_moderator_or_oauth_required_loged_in_from_reddit_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          oth.get_settings, self.sr)

    def test_moderator_or_oauth_required_loged_in_from_submission_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        submission = oth.get_submission(url=self.comment_url)
        self.assertRaises(errors.ModeratorOrScopeRequired, submission.remove)

    def test_moderator_or_oauth_required_loged_in_from_subreddit_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        subreddit = oth.get_subreddit(self.sr)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          subreddit.get_settings)

    def test_moderator_required_multi(self):
        self.r.login(self.un, '1111')
        sub = self.r.get_subreddit('{0}+{1}'.format(self.sr, 'test'))
        self.assertRaises(errors.ModeratorRequired, sub.get_mod_queue)

    def test_require_access_failure(self):
        self.assertRaises(TypeError, decorators.restrict_access, scope=None,
                          oauth_only=True)
