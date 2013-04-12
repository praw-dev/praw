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

from __future__ import print_function

import pytest
import os

from helper import (configure, interactive_only, PRIV_SR, PRIV_SUBMISSION_ID,
                    prompt, reddit_only, REFRESH_TOKEN, SR, SUBREDDIT,
                    SUBMISSION_EDIT_ID, UN, USER_AGENT)
from praw import errors, Reddit
from praw.objects import Submission


site_name = (os.getenv('REDDIT_SITE') or 'reddit') + '_oauth_test'
R = Reddit(USER_AGENT, site_name=site_name, disable_update_check=True)
INVALID = Reddit(USER_AGENT, disable_update_check=True)


def setup_function(function):
    configure()


def teardown_function(function):
    R.clear_authentication()


def test_authorize_url():
    url, params = R.get_authorize_url('...').split('?', 1)
    assert 'api/v1/authorize/' in url
    params = dict(x.split('=', 1) for x in params.split('&'))
    expected = {'client_id': R.config.client_id,
                'duration': 'temporary',
                'redirect_uri': ('http%3A%2F%2F127.0.0.1%3A65010%2F'
                                 'authorize_callback'),
                'response_type': 'code', 'scope': 'identity',
                'state': '...'}
    assert expected == params


@interactive_only
def test_get_access_information():
    print('Visit this URL: {0}'.format(R.get_authorize_url('...')))
    code = prompt('Code from redir URL: ')
    token = R.get_access_information(code)
    expected = {'access_token': R.access_token,
                'refresh_token': None,
                'scope': set(('identity',))}
    assert expected == token
    assert R.user is not None


def test_get_access_information_with_invalid_code():
    with pytest.raises(errors.OAuthInvalidGrant):
        R.get_access_information('invalid_code')


def test_invalid_app_access_token():
    with pytest.raises(errors.OAuthAppRequired):
        INVALID.get_access_information('dummy_code')


def test_invalid_app_authorize_url():
    with pytest.raises(errors.OAuthAppRequired):
        INVALID.get_authorize_url('dummy_state')


def test_invalid_set_access_credentials():
    with pytest.raises(errors.OAuthInvalidToken):
        R.set_access_credentials(set(('identity',)), 'dummy_access_token')


@reddit_only
def test_scope_edit():
    R.refresh_access_information(REFRESH_TOKEN['edit'])
    submission = Submission.from_id(R, SUBMISSION_EDIT_ID)
    assert submission == submission.edit('Edited text')


@reddit_only
def test_scope_identity():
    R.refresh_access_information(REFRESH_TOKEN['identity'])
    assert UN == R.get_me().name


@reddit_only
def test_scope_modconfig():
    R.refresh_access_information(REFRESH_TOKEN['modconfig'])
    SUBREDDIT.set_settings('foobar')


@reddit_only
def test_scope_modflair():
    R.refresh_access_information(REFRESH_TOKEN['modflair'])
    SUBREDDIT.set_flair(UN, 'foobar')


@reddit_only
def test_scope_modlog():
    R.refresh_access_information(REFRESH_TOKEN['modlog'])
    assert 25 == len(list(SUBREDDIT.get_mod_log()))


@reddit_only
def test_scope_modposts():
    R.refresh_access_information(REFRESH_TOKEN['modposts'])
    Submission.from_id(R, SUBMISSION_EDIT_ID).remove()


@reddit_only
def test_scope_mysubreddits():
    R.refresh_access_information(REFRESH_TOKEN['mysubreddits'])
    assert list(R.get_my_moderation())


@reddit_only
def test_scope_privatemessages():
    R.refresh_access_information(
        REFRESH_TOKEN['privatemessages'])
    assert list(R.get_inbox())


@reddit_only
def test_scope_read():
    R.refresh_access_information(REFRESH_TOKEN['read'])
    assert R.get_subreddit(PRIV_SR).subscribers > 0
    fullname = '{0}_{1}'.format(R.config.by_object[Submission],
                                PRIV_SUBMISSION_ID)
    method1 = R.get_info(thing_id=fullname)
    method2 = R.get_submission(submission_id=PRIV_SUBMISSION_ID)
    assert method1 == method2


@reddit_only
def test_scope_read_get_front_page():
    R.refresh_access_information(REFRESH_TOKEN['mysubreddits'])
    subscribed = list(R.get_my_reddits(limit=None))
    R.refresh_access_information(REFRESH_TOKEN['read'])
    assert all(post.subreddit in subscribed for post in R.get_front_page())


@reddit_only
def test_scope_read_get_sub_listingr():
    R.refresh_access_information(REFRESH_TOKEN['read'])
    subreddit = R.get_subreddit(PRIV_SR)
    assert len(list(subreddit.get_top()))


@reddit_only
def test_scope_read_get_submission_by_url():
    url = ("http://www.reddit.com/r/reddit_api_test_priv/comments/16kbb7/"
           "google/")
    R.refresh_access_information(REFRESH_TOKEN['read'])
    submission = Submission.from_url(R, url)
    assert submission.num_comments != 0


@reddit_only
def test_scope_read_priv_sr_comments():
    R.refresh_access_information(REFRESH_TOKEN['read'])
    assert len(list(R.get_comments(PRIV_SR)))


@reddit_only
def test_scope_read_priv_sub_comments():
    R.refresh_access_information(REFRESH_TOKEN['read'])
    submission = Submission.from_id(R, PRIV_SUBMISSION_ID)
    assert len(list(submission.comments))


@reddit_only
def test_scope_submit():
    R.refresh_access_information(REFRESH_TOKEN['submit'])
    retval = R.submit(SR, 'OAuth Submit', text='Foo')
    assert isinstance(retval, Submission)


@reddit_only
def test_scope_subscribe():
    R.refresh_access_information(REFRESH_TOKEN['subscribe'])
    SUBREDDIT.subscribe()


@reddit_only
def test_scope_vote():
    R.refresh_access_information(REFRESH_TOKEN['vote'])
    submission = Submission.from_id(R, SUBMISSION_EDIT_ID)
    submission.clear_vote()


@reddit_only
def test_set_access_credentials():
    assert R.user is None
    retval = R.refresh_access_information(REFRESH_TOKEN['identity'],
                                          update_session=False)
    assert R.user is None
    R.set_access_credentials(**retval)
    assert R.user is not None


@reddit_only
def test_oauth_without_identy_doesnt_set_user():
    assert R.user is None
    R.refresh_access_information(REFRESH_TOKEN['edit'])
    assert R.user is None


def test_set_oauth_info():
    with pytest.raises(errors.OAuthAppRequired):
        INVALID.get_authorize_url('dummy_state')
    INVALID.set_oauth_app_info(R.client_id, R.client_secret,
                               R.redirect_uri)
    INVALID.get_authorize_url('dummy_state')
