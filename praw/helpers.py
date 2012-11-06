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

"""Helper functions"""

import sys
import six
from requests.compat import urljoin
from praw.decorators import Memoize, SleepAfter, require_login


def _get_section(subpath=''):
    """Generate sections overview, comments and submitted for Redditor class"""
    def _section(self, sort='new', time='all', *args, **kwargs):
        if 'url_data' in kwargs and kwargs['url_data']:
            url_data = kwargs['url_data']
        else:
            url_data = kwargs['url_data'] = {}
        url_data.setdefault('sort', sort)
        url_data.setdefault('t', time)
        url = urljoin(self._url, subpath)  # pylint: disable-msg=W0212
        return self.reddit_session.get_content(url, *args, **kwargs)
    return _section


def _get_sorter(subpath='', **defaults):
    """Generate a Submission listing function."""
    def _sorted(self, *args, **kwargs):
        if 'url_data' in kwargs and kwargs['url_data']:
            url_data = kwargs['url_data']
        else:
            url_data = kwargs['url_data'] = {}
        for key, value in six.iteritems(defaults):
            url_data.setdefault(key, value)
        url = urljoin(self._url, subpath)  # pylint: disable-msg=W0212
        return self.reddit_session.get_content(url, *args, **kwargs)
    return _sorted


def _modify_relationship(relationship, unlink=False, is_sub=False):
    """
    Modify relationship.

    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit).
    """
    # the API uses friend and unfriend to manage all of these relationships
    url_key = 'unfriend' if unlink else 'friend'

    @require_login
    def do_relationship(thing, user):
        params = {'name': six.text_type(user),
                  'type': relationship}
        if is_sub:
            params['r'] = six.text_type(thing)
        else:
            params['container'] = thing.content_id
        url = thing.reddit_session.config[url_key]
        return thing.reddit_session.request_json(url, params)
    return do_relationship


@Memoize
@SleepAfter
def _request(reddit_session, page_url, params=None, data=None, timeout=45):
    """Make the http request and return the http response body."""
    if reddit_session.config.log_requests >= 1:
        sys.stderr.write('retrieving: %s\n' % page_url)
    if reddit_session.config.log_requests >= 2:
        sys.stderr.write('params: %s\n' % (params or 'None'))
        sys.stderr.write('data: %s\n' % (data or 'None'))

    if data:
        if data is True:
            data = {}
        data.setdefault('api_type', 'json')
        if reddit_session.modhash:
            data.setdefault('uh', reddit_session.modhash)
        method = reddit_session.http.post
    else:
        method = reddit_session.http.get
    response = method(page_url, params=params, data=data, timeout=timeout,
                      headers=reddit_session.DEFAULT_HEADERS)
    response.raise_for_status()
    return response.text
