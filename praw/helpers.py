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

from praw.compat import (Request, quote,  # pylint: disable-msg=E0611
                         urlencode, urljoin)
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
def _request(reddit_session, page_url, params=None, url_data=None, timeout=45):
    """Make the http request and return the http response body."""
    page_url = quote(page_url.encode('utf-8'), ':/')
    if url_data:
        page_url += '?' + urlencode(url_data)
    encoded_params = None
    if params:
        if params is True:
            params = {}
        params.setdefault('api_type', 'json')
        if reddit_session.modhash:
            params.setdefault('uh', reddit_session.modhash)
        params = dict([k, v.encode('utf-8')] for k, v in six.iteritems(params))
        encoded_params = urlencode(params).encode('utf-8')

    if reddit_session.access_token:
        headers = {"Authorization": "bearer %s" % reddit_session.access_token}
        headers.update(reddit_session.DEFAULT_HEADERS)

        # Requests using OAuth for authorization must switch to using the oauth
        # domain.
        for prefix in (reddit_session.config._site_url,
                       reddit_session.config._ssl_url):
            if page_url.startswith(prefix):
                if reddit_session.config.log_requests >= 1:
                    sys.stderr.write(
                        'substituting %s for %s in url\n'
                        % (reddit_session.config._oauth_url, prefix))
                page_url = (
                    reddit_session.config._oauth_url + page_url[len(prefix):])
                break
    else:
        headers = reddit_session.DEFAULT_HEADERS

    request = Request(page_url, data=encoded_params, headers=headers)

    if reddit_session.config.log_requests >= 1:
        sys.stderr.write('retrieving: %s\n' % page_url)
    if reddit_session.config.log_requests >= 2:
        sys.stderr.write('data: %s\n' % (encoded_params or 'None'))

    # pylint: disable-msg=W0212
    response = reddit_session._opener.open(request, timeout=timeout)
    return response.read()
