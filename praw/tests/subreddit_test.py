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

from praw.tests.helper import configure, first, R, reddit_only, SR, SUBREDDIT


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_attribute_error():
    with pytest.raises(AttributeError):  # pylint: disable-msg=E1101
        getattr(SUBREDDIT, 'foo')


def test_get_my_contributions():
    found = first(R.get_my_contributions(),
                  lambda subreddit: text_type(subreddit) == SR)
    assert found is not None


def test_get_my_moderation():
    found = first(R.get_my_moderation(),
                  lambda subreddit: text_type(subreddit) == SR)
    assert found is not None


def test_get_my_reddits():
    assert all(text_type(subreddit) in subreddit._info_url
               for subreddit in R.get_my_reddits())


@reddit_only
def test_search():
    assert len(list(SUBREDDIT.search('test'))) > 0


def test_subscribe_and_verify():
    SUBREDDIT.subscribe()
    found = first(R.get_my_reddits(),
                  lambda subreddit: text_type(subreddit) == SR)
    assert found is not None


def test_subscribe_by_name_and_verify():
    R.subscribe(SR)
    found = first(R.get_my_reddits(),
                  lambda subreddit: text_type(subreddit) == SR)
    assert found is not None


def test_unsubscribe_and_verify():
    SUBREDDIT.unsubscribe()
    assert all(text_type(subreddit) != SR for subreddit in R.get_my_reddits())


def test_unsubscribe_by_name_and_verify():
    R.unsubscribe(SR)
    assert all(text_type(subreddit) != SR for subreddit in R.get_my_reddits())
