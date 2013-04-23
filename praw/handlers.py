"""Provides classes that handle request dispatching."""
import socket
import time
from functools import wraps
from praw.helpers import normalize_url
from requests import Session
from six.moves import cPickle


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
    def wrapped(obj, _cache_key, _cache_ignore, _cache_timeout, **kwargs):
        if _cache_ignore:
            return function(obj, **kwargs)
        call_time = time.time()
        obj.clear_timeouts(call_time, _cache_timeout)
        obj.timeouts.setdefault(_cache_key, call_time)  # Does not update
        if _cache_key in obj.cache:
            return obj.cache[_cache_key]
        result = function(obj, **kwargs)
        return obj.cache.setdefault(_cache_key, result)
    return wrapped


class DefaultHandler(object):

    """Provides a basic request handler and cache for single-threaded PRAW.

    Rate-limits are enforced on a per-domain basis.

    """

    # The cache is class-level not instance level
    cache = {}
    timeouts = {}
    http = Session()

    @classmethod
    def clear_cache(cls):
        """Clear the entire cache."""
        cls.cache = {}
        cls.timeouts = {}

    @classmethod
    def clear_timeouts(cls, call_time, cache_timeout):
        """Clear the cache of timed out results."""
        for key in list(cls.timeouts):
            if call_time - cls.timeouts[key] > cache_timeout:
                del cls.timeouts[key]
                del cls.cache[key]

    @classmethod
    def evict(cls, urls):
        """Remove cached responses by URL."""
        urls = set(normalize_url(url) for url in urls)
        for key in list(cls.cache):
            if key[0] in urls:
                del cls.cache[key]
                del cls.timeouts[key]

    @use_cache
    @rate_limit
    def request(self, request, proxies=None, timeout=45):
        """Make the http request and return the http response."""
        return self.http.send(request, proxies=proxies, timeout=timeout)


class MultiprocessHandler(object):

    """A PRAW handler to interact with the PRAW multi-process server."""

    def __init__(self, host='localhost', port=10101):
        self.host = host
        self.port = port

    def _relay(self, **kwargs):
        """Send the request through the Server and return the http response."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            sock.sendall(cPickle.dumps(kwargs, cPickle.HIGHEST_PROTOCOL))
            response = ''
            while True:
                tmp = sock.recv(1024)
                if not tmp:
                    break
                response += tmp
            return cPickle.loads(response)
        finally:
            sock.close()

    def clear_cache(self):
        """We don't have a cache yet, so this does nothing."""

    def evict(self, urls):
        """We don't have a cache yet, so this does nothing."""

    def request(self, **kwargs):
        """Make the http request and return the http response."""
        return self._relay(method='request', **kwargs)
