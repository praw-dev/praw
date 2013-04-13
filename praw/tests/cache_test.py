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

import uuid
from six import next as six_next

from praw.tests.helper import configure, disable_cache, R, SR


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_cache():
    subreddit = R.get_subreddit(SR)
    title = 'Test Cache: %s' % uuid.uuid4()
    body = "BODY"
    original_listing = list(subreddit.get_new(limit=5))
    subreddit.submit(title, body)
    new_listing = list(subreddit.get_new(limit=5))
    assert original_listing == new_listing
    disable_cache()
    no_cache_listing = list(subreddit.get_new(limit=5))
    assert original_listing != no_cache_listing


def test_refresh_subreddit():
    disable_cache()
    subreddit = R.get_subreddit(SR)
    new_description = 'Description %s' % uuid.uuid4()
    subreddit.update_settings(public_description=new_description)
    assert new_description != subreddit.public_description
    subreddit.refresh()
    assert new_description == subreddit.public_description


def test_refresh_submission():
    disable_cache()
    subreddit = R.get_subreddit(SR)
    submission = six_next(subreddit.get_top())
    same_submission = R.get_submission(submission_id=submission.id)
    if submission.likes:
        submission.downvote()
    else:
        submission.upvote()
    assert submission.likes == same_submission.likes
    submission.refresh()
    assert submission.likes != same_submission.likes
