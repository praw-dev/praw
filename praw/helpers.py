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
from praw.decorators import Memoize, SleepAfter, restrict_access


def _get_section(subpath=''):
    """Return function to generate various non-subreddit listings."""
    def _section(self, sort='new', time='all', *args, **kwargs):
        if not kwargs.get('params'):
            kwargs['params'] = {}
        kwargs['params'].setdefault('sort', sort)
        kwargs['params'].setdefault('t', time)
        url = urljoin(self._url, subpath)  # pylint: disable-msg=W0212
        return self.reddit_session.get_content(url, *args, **kwargs)
    return _section


def _get_sorter(subpath='', **defaults):
    """Return function to generate specific subreddit Submission listings."""
    def _sorted(self, *args, **kwargs):
        if not kwargs.get('params'):
            kwargs['params'] = {}
        for key, value in six.iteritems(defaults):
            kwargs['params'].setdefault(key, value)
        url = urljoin(self._url, subpath)  # pylint: disable-msg=W0212
        return self.reddit_session.get_content(url, *args, **kwargs)
    return _sorted


def _modify_relationship(relationship, unlink=False, is_sub=False):
    """Return a function for relationship modification.

    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit).

    """
    # the API uses friend and unfriend to manage all of these relationships
    url_key = 'unfriend' if unlink else 'friend'

    if relationship == 'friend':
        access = {'scope': None, 'login': True}
    else:
        access = {'scope': None, 'mod': True}

    @restrict_access(**access)
    def do_relationship(thing, user):
        data = {'name': six.text_type(user),
                'type': relationship}
        if is_sub:
            data['r'] = six.text_type(thing)
        else:
            data['container'] = thing.fullname

        if relationship == 'moderator':
            _request.evict([thing.reddit_session.config['moderators'] %
                            six.text_type(thing)])
        url = thing.reddit_session.config[url_key]
        return thing.reddit_session.request_json(url, data=data)
    return do_relationship


@Memoize
@SleepAfter
def _request(reddit_session, url, params=None, data=None, timeout=45,
             raw_response=False, auth=None, files=None):
    """Make the http request and return the http response body."""
    if not auth and reddit_session.access_token:
        headers = {'Authorization': 'bearer %s' % reddit_session.access_token}
        # Requests using OAuth for authorization must switch to using the oauth
        # domain.
        # pylint: disable-msg=W0212
        for prefix in (reddit_session.config._site_url,
                       reddit_session.config._ssl_url):
            if url.startswith(prefix):
                if reddit_session.config.log_requests >= 1:
                    sys.stderr.write(
                        'substituting %s for %s in url\n'
                        % (reddit_session.config._oauth_url, prefix))
                url = (reddit_session.config._oauth_url + url[len(prefix):])
                break
    else:
        headers = {}

    if reddit_session.config.log_requests >= 1:
        sys.stderr.write('retrieving: %s\n' % url)
    if reddit_session.config.log_requests >= 2:
        sys.stderr.write('params: %s\n' % (params or 'None'))
        sys.stderr.write('data: %s\n' % (data or 'None'))
        if auth:
            sys.stderr.write('auth: %s\n' % auth)

    if data or files:
        if data is True:
            data = {}
        if not auth:
            data.setdefault('api_type', 'json')
            if reddit_session.modhash:
                data.setdefault('uh', reddit_session.modhash)
        method = reddit_session.http.post
    else:
        method = reddit_session.http.get

    response = None
    while True:
        # pylint: disable-msg=W0212
        try:
            response = method(url, params=params, data=data, files=files,
                              headers=headers, timeout=timeout,
                              allow_redirects=False, auth=auth)
        finally:
            # Hack to force-close the connection (if needed) until
            # https://github.com/shazow/urllib3/pull/133 is added to urllib3
            # and then the version of urllib3 in requests is updated We also
            # have to manually handle redirects for now because of this.
            if response and response.raw._fp.will_close:
                response.raw._fp.close()
        if response.status_code == 302:
            url = urljoin(url, response.headers['location'])
        else:
            break
    response.raise_for_status()
    if raw_response:
        return response
    return response.text
