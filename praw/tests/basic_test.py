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

from requests.exceptions import Timeout
import pytest

from praw import helpers, Reddit
from praw.objects import Comment, MoreComments, Submission
from praw.tests.helper import (COMMENT_URL, INVALID_USER_NAME, LINK_URL,
                               LINK_URL_LINK, R, SR, UN, reddit_only)


def test_comments_contains_no_noncomment_objects():
    comments = R.get_submission(url=COMMENT_URL).comments
    assert not [item for item in comments if not
                (isinstance(item, Comment) or isinstance(item, MoreComments))]


def test_decode_entities():
    text = R.get_submission(url=COMMENT_URL).selftext_html
    assert text.startswith('&lt;')
    assert text.endswith('&gt;')
    R.config.decode_html_entities = True
    text = R.get_submission(url=COMMENT_URL).selftext_html
    assert text.startswith('<')
    assert text.endswith('>')


def test_equality():
    subreddit = R.get_subreddit(SR)
    same_subreddit = R.get_subreddit(SR)
    submission = next(subreddit.get_hot())
    assert subreddit == same_subreddit
    assert not subreddit != same_subreddit
    assert not subreddit == submission


def test_get_all_comments():
    num = 50
    assert num == len(list(R.get_all_comments(limit=num)))


def test_get_all_comments_gilded():
    gilded_comments = R.get_all_comments(gilded_only=True)
    assert all(comment.gilded > 0 for comment in gilded_comments)


def test_get_comments():
    num = 50
    result = R.get_comments(SR, limit=num)
    assert num == len(list(result))


@reddit_only
def test_get_controversial():
    num = 50
    result = R.get_controversial(limit=num, params={'t': 'all'})
    assert num == len(list(result))


def test_get_flair_list():
    sub = R.get_subreddit('python')
    assert next(sub.get_flair_list())


def test_get_front_page():
    num = 50
    assert num == len(list(R.get_front_page(limit=num)))


def test_get_new():
    num = 50
    result = R.get_new(limit=num, params={'sort': 'new'})
    assert num == len(list(result))


@reddit_only
def test_get_popular_reddits():
    num = 50
    assert num == len(list(R.get_popular_reddits(limit=num)))


def test_get_random_subreddit():
    subs = set()
    for _ in range(3):
        subs.add(R.get_subreddit('RANDOM').display_name)
    assert len(subs) > 1


def test_get_submissions():
    kind = R.config.by_object[Submission]

    def fullname(url):
        return '{0}_{1}'.format(kind, url.rsplit('/', 2)[1])
    fullnames = [fullname(COMMENT_URL), fullname(LINK_URL)] * 100
    retreived = [x.fullname for x in R.get_submissions(fullnames)]
    assert fullnames == retreived


@reddit_only
def test_get_top():
    num = 50
    result = R.get_top(limit=num, params={'t': 'all'})
    assert num == len(list(result))


def test_info_by_invalid_id():
    assert None == R.get_info(thing_id='INVALID')


def test_info_by_known_url_returns_known_id_link_post():
    found_links = R.get_info(LINK_URL_LINK)
    tmp = R.get_submission(url=LINK_URL)
    assert tmp in found_links


def test_info_by_url_also_found_by_id():
    found_by_url = R.get_info(LINK_URL_LINK)[0]
    found_by_id = R.get_info(thing_id=found_by_url.fullname)
    assert found_by_id == found_by_url


@reddit_only
def test_info_by_url_maximum_listing():
    assert 100 == len(R.get_info('http://www.reddit.com', limit=101))


def test_is_username_available():
    assert not R.is_username_available(UN)
    assert R.is_username_available(INVALID_USER_NAME)
    assert not R.is_username_available('')


def test_not_logged_in_when_initialized():
    assert R.user is None


def test_require_user_agent():
    with pytest.raises(TypeError):  # pylint: disable-msg=E1101
        Reddit(user_agent=None)
    with pytest.raises(TypeError):  # pylint: disable-msg=E1101
        Reddit(user_agent='')
    with pytest.raises(TypeError):  # pylint: disable-msg=E1101
        Reddit(user_agent=1)


@reddit_only
def test_search():
    assert len(list(R.search('test'))) > 0


def test_search_reddit_names():
    assert len(R.search_reddit_names('reddit')) > 0


def test_timeout():
    with pytest.raises(Timeout):  # pylint: disable-msg=E1101
        helpers._request(R, R.config['comments'], timeout=0.001)
