"""Provides classes that handle request dispatching."""
import time
from functools import wraps
from requests.compat import urljoin
from praw.errors import (ClientException, InvalidSubreddit, OAuthException,
                         OAuthInsufficientScope, OAuthInvalidToken)
from praw.helpers import normalize_url


def rate_limit(function):
    """Return a decorator that enforces API request limit guidelines.

    We are allowed to make a API request every api_request_delay seconds as
    specified in praw.ini. This value may differ from reddit to reddit. For
    reddit.com it is 2. Any function decorated with this will be forced to
    delay api_request_delay seconds from the calling of the last function
    decorated with this before executing.

    """
    @wraps(function)
    def wrapped(obj, _rate_domain, _rate_delay, **kwargs):
        last = last_call.get(_rate_domain, 0)
        now = time.time()
        delay = last + _rate_delay - now
        if delay > 0:
            now += delay
            time.sleep(delay)
        last_call[_rate_domain] = now
        return function(obj, **kwargs)
    last_call = {}
    return wrapped


def use_cache(function):
    """Return a decorator that interacts with a handler's cache."""
    @wraps(function)
    def wrapped(obj, url, _cache_key, _cache_timeout, **kwargs):
        if kwargs.get('files') or kwargs.get('raw_response'):
            # Ignore file uploads or raw_response requests
            return function(obj, url=url, **kwargs)
        call_time = time.time()
        obj.clear_timeouts(call_time, _cache_timeout)
        obj.timeouts.setdefault(_cache_key, call_time)  # Does not update
        if _cache_key in obj.cache:
            return obj.cache[_cache_key]
        result = function(obj, url=url, **kwargs)
        return obj.cache.setdefault(_cache_key, result)
    return wrapped


class DefaultHandler(object):

    """Provides a basic request handler and cache for single-threaded PRAW.

    Rate-limits are enforced on a per-domain basis.

    """

    # The cache is class-level not instance level
    cache = {}
    timeouts = {}

    @staticmethod
    def _handle_redirect(url, response):
        """Return the new url or None if there are no redirects.

        Raise exceptions if appropriate.

        """
        if response.status_code != 302:
            return None
        new_url = urljoin(url, response.headers['location'])
        if 'reddits/search?q=' in new_url:  # Handle non-existent subreddit
            subreddit = new_url.rsplit('=', 1)[1]
            raise InvalidSubreddit('`{0}` is not a valid subreddit'
                                   .format(subreddit))
        elif 'random' not in url:
            raise ClientException('Unexpected redirect from {0} to {1}'
                                  .format(url, new_url))
        return new_url

    @staticmethod
    def _raise_exceptions(url, response):
        """Raise specific errors on some status codes."""
        if response.status_code != 200 and \
                'www-authenticate' in response.headers:
            msg = response.headers['www-authenticate']
            if 'insufficient_scope' in msg:
                raise OAuthInsufficientScope('insufficient_scope', url)
            elif 'invalid_token' in msg:
                raise OAuthInvalidToken('invalid_token', url)
            else:
                raise OAuthException(msg, url)
        response.raise_for_status()

    @classmethod
    def clear_cache(cls):
        """Clear the entire cache."""
        cls.cache = {}
        cls.timeouts = {}

    @classmethod
    def clear_timeouts(cls, call_time, cache_timeout):
        """Clear the cache of timed out results."""
        for key in cls.timeouts.keys():
            if call_time - cls.timeouts[key] > cache_timeout:
                del cls.timeouts[key]
                del cls.cache[key]

    @classmethod
    def evict(cls, urls):
        """Remove cached responses by URL."""
        urls = set(normalize_url(url) for url in urls)
        for key in cls.cache.keys():
            if key[0] in urls:
                del cls.cache[key]
                del cls.timeouts[key]

    @use_cache
    @rate_limit
    def request(self, url, method, params=None, data=None, files=None,
                headers=None, auth=None, timeout=45, raw_response=False):
        """Make the http request and return the http response body."""
        response = None
        request_url = url
        while request_url:  # Manually handle 302 redirects
            response = method(request_url, params=params, data=data,
                              files=files, headers=headers, timeout=timeout,
                              allow_redirects=False, auth=auth)
            url = request_url
            request_url = self._handle_redirect(request_url, response)
        self._raise_exceptions(url, response)
        if raw_response:
            return response
        return response.text
