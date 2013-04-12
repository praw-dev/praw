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

import uuid
import random
import pytest
from six import next as six_next, text_type
from requests.exceptions import HTTPError

from helper import configure, delay, flair_diff, INVALID_USER_NAME, R, SR
from praw import errors


def setup_function(function):
    configure()


def test_add_link_flair():
    subreddit = R.get_subreddit(SR)
    flair_text = 'Flair: %s' % uuid.uuid4()
    sub = six_next(subreddit.get_new())
    subreddit.set_flair(sub, flair_text)
    sub = R.get_submission(sub.permalink)
    assert sub.link_flair_text == flair_text


def test_add_link_flair_through_submission():
    subreddit = R.get_subreddit(SR)
    flair_text = 'Falir: %s' % uuid.uuid4()
    sub = six_next(subreddit.get_new())
    sub.set_flair(flair_text)
    sub = R.get_submission(sub.permalink)
    assert sub.link_flair_text == flair_text


def test_add_link_flair_to_invalid_subreddit():
    subreddit = R.get_subreddit(SR)
    sub = six_next(R.get_subreddit('python').get_new())
    with pytest.raises(HTTPError):
        subreddit.set_flair(sub, 'text')


def test_add_user_flair_by_subreddit_name():
    flair_text = 'Flair: %s' % uuid.uuid4()
    R.set_flair(SR, R.user, flair_text)
    flair = R.get_flair(SR, R.user)
    assert flair['flair_text'] == flair_text
    assert flair['flair_css_class'] is None


def test_add_user_flair_to_invalid_user():
    subreddit = R.get_subreddit(SR)
    with pytest.raises(errors.InvalidFlairTarget):
        subreddit.set_flair(INVALID_USER_NAME)


def test_add_user_flair_by_name():
    subreddit = R.get_subreddit(SR)
    flair_text = 'Flair: %s' % uuid.uuid4()
    flair_css = 'a%d' % random.randint(0, 1024)
    subreddit.set_flair(text_type(R.user), flair_text, flair_css)
    flair = subreddit.get_flair(R.user)
    assert flair['flair_text'] == flair_text
    assert flair['flair_css_class'] == flair_css


def test_clear_user_flair():
    subreddit = R.get_subreddit(SR)
    subreddit.set_flair(R.user)
    flair = subreddit.get_flair(R.user)
    assert flair['flair_text'] is None
    assert flair['flair_css_class'] is None


def test_delete_flair():
    subreddit = R.get_subreddit(SR)
    flair = list(subreddit.get_flair_list(limit=1))[0]
    subreddit.delete_flair(flair['user'])
    assert flair not in subreddit.get_flair_list()


def test_flair_csv_and_flair_list():
    # Clear all flair
    subreddit = R.get_subreddit(SR)
    subreddit.clear_all_flair()
    delay(5)  # Wait for flair to clear
    assert [] == list(subreddit.get_flair_list())

    # Set flair
    flair_mapping = [{'user': 'reddit', 'flair_text': 'dev'},
                     {'user': 'PyAPITestUser2', 'flair_css_class': 'xx'},
                     {'user': 'PyAPITestUser3', 'flair_text': 'AWESOME',
                     'flair_css_class': 'css'}]
    subreddit.set_flair_csv(flair_mapping)
    assert [] == flair_diff(flair_mapping, list(subreddit.get_flair_list()))


def test_flair_csv_many():
    subreddit = R.get_subreddit(SR)
    users = ('reddit', 'pyapitestuser2', 'pyapitestuser3')
    flair_text_a = 'Flair: %s' % uuid.uuid4()
    flair_text_b = 'Flair: %s' % uuid.uuid4()
    flair_mapping = [{'user': 'reddit', 'flair_text': flair_text_a}] * 99
    for user in users:
        flair_mapping.append({'user': user, 'flair_text': flair_text_b})
    subreddit.set_flair_csv(flair_mapping)
    for user in users:
        flair = subreddit.get_flair(user)
        assert flair['flair_text'] == flair_text_b


def test_flair_csv_optional_args():
    subreddit = R.get_subreddit(SR)
    flair_mapping = [{'user': 'reddit', 'flair_text': 'reddit'},
                     {'user': 'pyapitestuser3', 'flair_css_class': 'blah'}]
    subreddit.set_flair_csv(flair_mapping)


def test_flair_csv_empty():
    subreddit = R.get_subreddit(SR)
    with pytest.raises(errors.ClientException):
        subreddit.set_flair_csv([])


def test_flair_csv_requires_user():
    subreddit = R.get_subreddit(SR)
    flair_mapping = [{'flair_text': 'hsdf'}]
    with pytest.raises(errors.ClientException):
        subreddit.set_flair_csv(flair_mapping)
