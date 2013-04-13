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
import random
import pytest
from six import next as six_next, text_type
from requests.exceptions import HTTPError

from praw import errors
from praw.tests.helper import (configure, delay, flair_diff, INVALID_USER_NAME,
                               R, SR, SUBREDDIT)


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_add_link_flair():
    flair_text = 'Flair: %s' % uuid.uuid4()
    sub = six_next(SUBREDDIT.get_new())
    SUBREDDIT.set_flair(sub, flair_text)
    sub = R.get_submission(sub.permalink)
    assert sub.link_flair_text == flair_text


def test_add_link_flair_through_submission():
    flair_text = 'Falir: %s' % uuid.uuid4()
    sub = six_next(SUBREDDIT.get_new())
    sub.set_flair(flair_text)
    sub = R.get_submission(sub.permalink)
    assert sub.link_flair_text == flair_text


def test_add_link_flair_to_invalid_subreddit():
    sub = six_next(R.get_subreddit('python').get_new())
    with pytest.raises(HTTPError):  # pylint: disable-msg=E1101
        SUBREDDIT.set_flair(sub, 'text')


def test_add_user_flair_by_subreddit_name():
    flair_text = 'Flair: %s' % uuid.uuid4()
    R.set_flair(SR, R.user, flair_text)
    flair = R.get_flair(SR, R.user)
    assert flair['flair_text'] == flair_text
    assert flair['flair_css_class'] is None


def test_add_user_flair_to_invalid_user():
    with pytest.raises(errors.InvalidFlairTarget):  # pylint: disable-msg=E1101
        SUBREDDIT.set_flair(INVALID_USER_NAME)


def test_add_user_flair_by_name():
    flair_text = 'Flair: %s' % uuid.uuid4()
    flair_css = 'a%d' % random.randint(0, 1024)
    SUBREDDIT.set_flair(text_type(R.user), flair_text, flair_css)
    flair = SUBREDDIT.get_flair(R.user)
    assert flair['flair_text'] == flair_text
    assert flair['flair_css_class'] == flair_css


def test_clear_user_flair():
    SUBREDDIT.set_flair(R.user)
    flair = SUBREDDIT.get_flair(R.user)
    assert flair['flair_text'] is None
    assert flair['flair_css_class'] is None


def test_delete_flair():
    flair = list(SUBREDDIT.get_flair_list(limit=1))[0]
    SUBREDDIT.delete_flair(flair['user'])
    assert flair not in SUBREDDIT.get_flair_list()


def test_flair_csv_and_flair_list():
    # Clear all flair
    SUBREDDIT.clear_all_flair()
    delay(5)  # Wait for flair to clear
    assert [] == list(SUBREDDIT.get_flair_list())

    # Set flair
    flair_mapping = [{'user': 'reddit', 'flair_text': 'dev'},
                     {'user': 'PyAPITestUser2', 'flair_css_class': 'xx'},
                     {'user': 'PyAPITestUser3', 'flair_text': 'AWESOME',
                     'flair_css_class': 'css'}]
    SUBREDDIT.set_flair_csv(flair_mapping)
    assert [] == flair_diff(flair_mapping, list(SUBREDDIT.get_flair_list()))


def test_flair_csv_many():
    users = ('reddit', 'pyapitestuser2', 'pyapitestuser3')
    flair_text_a = 'Flair: %s' % uuid.uuid4()
    flair_text_b = 'Flair: %s' % uuid.uuid4()
    flair_mapping = [{'user': 'reddit', 'flair_text': flair_text_a}] * 99
    for user in users:
        flair_mapping.append({'user': user, 'flair_text': flair_text_b})
    SUBREDDIT.set_flair_csv(flair_mapping)
    for user in users:
        flair = SUBREDDIT.get_flair(user)
        assert flair['flair_text'] == flair_text_b


def test_flair_csv_optional_args():
    flair_mapping = [{'user': 'reddit', 'flair_text': 'reddit'},
                     {'user': 'pyapitestuser3', 'flair_css_class': 'blah'}]
    SUBREDDIT.set_flair_csv(flair_mapping)


def test_flair_csv_empty():
    with pytest.raises(errors.ClientException):  # pylint: disable-msg=E1101
        SUBREDDIT.set_flair_csv([])


def test_flair_csv_requires_user():
    flair_mapping = [{'flair_text': 'hsdf'}]
    with pytest.raises(errors.ClientException):  # pylint: disable-msg=E1101
        SUBREDDIT.set_flair_csv(flair_mapping)
