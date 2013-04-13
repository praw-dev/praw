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

from praw import decorators, errors, Reddit
from praw.tests.helper import COMMENT_URL, R, SR, UN, USER_AGENT


def teardown_function(function):  # pylint: disable-msg=W0613
    R.clear_authentication()


def test_exception_get_flair_list_authenticated():
    R.login(UN, '1111')
    assert R.get_flair_list(SR)


def test_exception_get_flair_list_unauthenticated():
    assert R.get_flair_list(SR)


def test_login_or_oauth_required_not_logged_in():
    # pylint: disable-msg=E1101
    with pytest.raises(errors.LoginOrScopeRequired):
        R.add_flair_template(SR, 'foo')


def test_login_or_oauth_required_not_logged_in_mod_func():
    # pylint: disable-msg=E1101
    with pytest.raises(errors.LoginOrScopeRequired):
        R.get_settings(SR)


def test_login_required_not_logged_in():
    with pytest.raises(errors.LoginRequired):  # pylint: disable-msg=E1101
        R.accept_moderator_invite(SR)


def test_login_required_not_logged_in_mod_func():
    with pytest.raises(errors.LoginRequired):  # pylint: disable-msg=E1101
        R.get_banned(SR)


def test_oauth_scope_required():
    R.set_oauth_app_info('dummy_client', 'dummy_secret', 'dummy_url')
    R.set_access_credentials(set('dummy_scope',), 'dummy_token')
    # pylint: disable-msg=E1101
    with pytest.raises(errors.OAuthScopeRequired):
        R.get_me()


def test_moderator_or_oauth_required_loged_in_from_reddit_obj():
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    # pylint: disable-msg=E1101
    with pytest.raises(errors.ModeratorOrScopeRequired):
        oth.get_settings(SR)


def test_moderator_or_oauth_required_loged_in_from_submission_obj():
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    submission = oth.get_submission(url=COMMENT_URL)
    # pylint: disable-msg=E1101
    with pytest.raises(errors.ModeratorOrScopeRequired):
        submission.remove()


def test_moderator_or_oauth_required_loged_in_from_subreddit_obj():
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    subreddit = oth.get_subreddit(SR)
    # pylint: disable-msg=E1101
    with pytest.raises(errors.ModeratorOrScopeRequired):
        subreddit.get_settings()


def test_moderator_required_multi():
    R.login(UN, '1111')
    sub = R.get_subreddit('{0}+{1}'.format(SR, 'test'))
    # pylint: disable-msg=E1101
    with pytest.raises(errors.ModeratorRequired):
        sub.get_mod_queue()


def test_require_access_failure():
    with pytest.raises(TypeError):  # pylint: disable-msg=E1101
        decorators.restrict_access(scope=None, oauth_only=True)
