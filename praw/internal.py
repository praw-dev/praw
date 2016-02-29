"""Internal helper functions.

The functions in this module are not to be relied upon by third-parties.

"""
import re
import sys

import six
from requests import Request, codes, exceptions
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from .errors import (HTTPException, Forbidden, NotFound, InvalidSubreddit,
                     OAuthException, OAuthInsufficientScope,
                     OAuthInvalidToken, RedirectException)


RE_REDIRECT = re.compile('(rand(om|nsfw))|about/sticky')


def _modify_relationship(relationship, unlink=False, is_sub=False):
    """Return a function for relationship modification.

    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit).

    """
    # The API uses friend and unfriend to manage all of these relationships.
    url_key = 'unfriend' if unlink else 'friend'

    def do_relationship(thing, user, **kwargs):
        data = {'name': six.text_type(user),
                'type': relationship}
        data.update(kwargs)
        if is_sub:
            data['r'] = six.text_type(thing)
        else:
            data['container'] = thing.fullname

        session = thing.reddit_session
        url = session.config[url_key]
        return session.request_json(url, data=data)
    return do_relationship


def _prepare_request(reddit_session, url, params, data, auth, files,
                     method=None):
    """Return a requests Request object that can be "prepared"."""
    if method:
        pass
    elif data or files:
        method = 'POST'
    else:
        method = 'GET'

    # Log the request if logging is enabled
    if reddit_session.config.log_requests >= 1:
        sys.stderr.write('{0}: {1}\n'.format(method, url))
    if reddit_session.config.log_requests >= 2:
        if params:
            sys.stderr.write('params: {0}\n'.format(params))
        if data:
            sys.stderr.write('data: {0}\n'.format(data))
        if auth:
            sys.stderr.write('auth: {0}\n'.format(auth))
    # Prepare request
    request = Request(method=method, url=url,
                      headers=reddit_session.http.headers, params=params,
                      auth=auth, cookies=reddit_session.http.cookies)
    if method == 'GET':
        return request
    # Most POST requests require adding `api_type` and `uh` to the data.
    if data is True:
        data = {}

    request.data = data
    request.files = files
    return request


def _raise_redirect_exceptions(response):
    """Return the new url or None if there are no redirects.

    Raise exceptions if appropriate.

    """
    if response.status_code not in [301, 302, 307]:
        return None
    new_url = urljoin(response.url, response.headers['location'])
    if 'reddits/search' in new_url:  # Handle non-existent subreddit
        subreddit = new_url.rsplit('=', 1)[1]
        raise InvalidSubreddit('`{0}` is not a valid subreddit'
                               .format(subreddit))
    elif not RE_REDIRECT.search(response.url):
        raise RedirectException(response.url, new_url)
    return new_url


def _raise_response_exceptions(response):
    """Raise specific errors on some status codes."""
    if not response.ok and 'www-authenticate' in response.headers:
        msg = response.headers['www-authenticate']
        if 'insufficient_scope' in msg:
            raise OAuthInsufficientScope('insufficient_scope', response.url)
        elif 'invalid_token' in msg:
            raise OAuthInvalidToken('invalid_token', response.url)
        else:
            raise OAuthException(msg, response.url)

    if response.status_code == codes['forbidden']:
        raise Forbidden(_raw=response)
    elif response.status_code == codes['not_found']:
        raise NotFound(_raw=response)
    else:
        try:
            response.raise_for_status()  # These should all be directly mapped
        except exceptions.HTTPError as exc:
            raise HTTPException(_raw=exc.response)


def _to_reddit_list(arg):
    """Return an argument converted to a reddit-formatted list.

    The returned format is a comma deliminated list. Each element is a string
    representation of an object. Either given as a string or as an object that
    is then converted to its string representation.
    """
    if (isinstance(arg, six.string_types) or not (
            hasattr(arg, "__getitem__") or hasattr(arg, "__iter__"))):
        return six.text_type(arg)
    else:
        return ','.join(six.text_type(a) for a in arg)
