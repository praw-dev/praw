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

"""Internal helper functions."""

from requests import Request
import six
import sys
from warnings import warn
from requests.compat import urljoin
from praw.decorators import restrict_access
from praw.errors import (InvalidSubreddit, OAuthException,
                         OAuthInsufficientScope, OAuthInvalidToken,
                         RedirectException)


def _get_section(subpath=''):
    """Return function to generate various non-subreddit listings."""
    def _section(self, sort='new', time='all', *args, **kwargs):
        """Return a get_content generator for some RedditContentObject type.

        :param sort: Specify the sort order of the results if applicable.
        :param time: Specify the time-period to return submissions if
            applicable.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        kwargs.setdefault('params', {})
        kwargs['params'].setdefault('sort', sort)
        kwargs['params'].setdefault('t', time)
        url = urljoin(self._url, subpath)  # pylint: disable-msg=W0212
        return self.reddit_session.get_content(url, *args, **kwargs)
    return _section


def _get_sorter(subpath='', deprecated=False, **defaults):
    """Return function to generate specific subreddit Submission listings."""
    @restrict_access(scope='read')
    def _sorted(self, *args, **kwargs):
        """Return a get_content generator for some RedditContentObject type.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """

        if deprecated:
            warn('Please use `{0}` instead'.format(deprecated),
                 DeprecationWarning)
        if not kwargs.get('params'):
            kwargs['params'] = {}
        for key, value in six.iteritems(defaults):
            kwargs['params'].setdefault(key, value)
        url = urljoin(self._url, subpath)  # pylint: disable-msg=W0212
        return self.reddit_session.get_content(url, *args, **kwargs)
    return _sorted


def _modify_relationship(relationship, unlink=False, is_sub=False,
                         deprecated=False):
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
        if deprecated:
            warn('Please use `{0}` instead'.format(deprecated),
                 DeprecationWarning)

        data = {'name': six.text_type(user),
                'type': relationship}
        if is_sub:
            data['r'] = six.text_type(thing)
        else:
            data['container'] = thing.fullname

        session = thing.reddit_session
        if relationship == 'moderator':
            session.evict(session.config['moderators'] % six.text_type(thing))
        url = session.config[url_key]
        return session.request_json(url, data=data)
    return do_relationship


def _prepare_request(reddit_session, url, params, data, auth, files):
    """Return a requests Request object that can be "prepared"."""
    # Requests using OAuth for authorization must switch to using the oauth
    # domain.
    if getattr(reddit_session, '_use_oauth', False):
        headers = {'Authorization': 'bearer %s' % reddit_session.access_token}
        config = reddit_session.config
        # pylint: disable-msg=W0212
        for prefix in (config._site_url, config._ssl_url):
            if url.startswith(prefix):
                if config.log_requests >= 1:
                    sys.stderr.write('substituting %s for %s in url\n'
                                     % (config._oauth_url, prefix))
                url = config._oauth_url + url[len(prefix):]
                break
    else:
        headers = {}
    headers.update(reddit_session.http.headers)
    # Log the request if logging is enabled
    if reddit_session.config.log_requests >= 1:
        sys.stderr.write('retrieving: %s\n' % url)
    if reddit_session.config.log_requests >= 2:
        sys.stderr.write('params: %s\n' % (params or 'None'))
        sys.stderr.write('data: %s\n' % (data or 'None'))
        if auth:
            sys.stderr.write('auth: %s\n' % str(auth))
    # Prepare request
    request = Request(method='GET', url=url, headers=headers, params=params,
                      auth=auth, cookies=reddit_session.http.cookies)
    if not data and not files:  # GET request
        return request
    # Most POST requests require adding `api_type` and `uh` to the data.
    if data is True:
        data = {}
    if not auth:
        data.setdefault('api_type', 'json')
        if reddit_session.modhash:
            data.setdefault('uh', reddit_session.modhash)
    request.method = 'POST'
    request.data = data
    request.files = files
    return request


def _raise_redirect_exceptions(response):
    """Return the new url or None if there are no redirects.

    Raise exceptions if appropriate.

    """
    if response.status_code != 302:
        return None
    new_url = urljoin(response.url, response.headers['location'])
    if 'reddits/search?q=' in new_url:  # Handle non-existent subreddit
        subreddit = new_url.rsplit('=', 1)[1]
        raise InvalidSubreddit('`{0}` is not a valid subreddit'
                               .format(subreddit))
    elif 'random' not in response.url:
        raise RedirectException(response.url, new_url)
    return new_url


def _raise_response_exceptions(response):
    """Raise specific errors on some status codes."""
    if response.status_code != 200 and \
            'www-authenticate' in response.headers:
        msg = response.headers['www-authenticate']
        if 'insufficient_scope' in msg:
            raise OAuthInsufficientScope('insufficient_scope', response.url)
        elif 'invalid_token' in msg:
            raise OAuthInvalidToken('invalid_token', response.url)
        else:
            raise OAuthException(msg, response.url)
    response.raise_for_status()
