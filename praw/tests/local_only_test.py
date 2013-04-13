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
import random

from praw import errors
from praw.tests.helper import configure, local_only, OTHER_USER_NAME, R, SR, UN


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


@local_only
def test_create_existing_redditor():
    R.login(UN, '1111')
    with pytest.raises(errors.UsernameExists):  # pylint: disable-msg=E1101
        R.create_redditor(OTHER_USER_NAME, '1111')


@local_only
def test_create_existing_subreddit():
    R.login(UN, '1111')
    with pytest.raises(errors.SubredditExists):  # pylint: disable-msg=E1101
        R.create_subreddit(SR, 'foo')


@local_only
def test_create_redditor():
    unique_name = 'PyAPITestUser%d' % random.randint(3, 10240)
    R.create_redditor(unique_name, '1111')


@local_only
def test_create_subreddit():
    unique_name = 'test%d' % random.randint(3, 10240)
    description = '#Welcome to %s\n\n0 item 1\n0 item 2\n' % unique_name
    R.login(UN, '1111')
    R.create_subreddit(unique_name, 'The %s' % unique_name, description)


@local_only
def test_failed_feedback():
    with pytest.raises(errors.InvalidEmails):  # pylint: disable-msg=E1101
        R.send_feedback('a', 'b', 'c')


@local_only
def test_send_feedback():
    msg = 'You guys are awesome. (Sent from the PRAW python module).'
    R.send_feedback('Bryce Boe', 'foo@foo.com', msg)
