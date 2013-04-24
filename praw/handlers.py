"""Provides classes that handle request dispatching."""
import socket
import time
from functools import wraps
from praw.helpers import normalize_url
from requests import Session
from six.moves import cPickle
from threading import Lock


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


class RateLimitHandler(object):

    """The base handler that provides thread-safe rate limiting enforcement.


    While this handler is threadsafe, PRAW is not thread safe when the same
    `Reddit` instance is being utilized from multiple threads.

    """

    last_call = {}  # Stores a two-item list: [lock, previous_call_time]
    lock = Lock()  # lock used for adding items to last_call

    def __init__(self):
        self.http = Session()  # Each instance should have its own session

    @classmethod
    def evict(cls, urls):
        """Method utilized to evict entries for the given urls.

        :param urls: An interable containing normalized urls.

        By default this method does nothing as a cache need not be present.

        """

    @staticmethod
    def rate_limit(function):
        """Return a decorator that enforces API request limit guidelines.

        We are allowed to make a API request every api_request_delay seconds as
        specified in praw.ini. This value may differ from reddit to reddit. For
        reddit.com it is 2. Any function decorated with this will be forced to
        delay _rate_delay seconds from the calling of the last function
        decorated with this before executing.

        This decorator must be applied to a RateLimitHandler class method or
        instance method as it assumes `lock` and `last_call` are available.

        """
        @wraps(function)
        def wrapped(cls, _rate_domain, _rate_delay, **kwargs):
            cls.lock.acquire()
            lock_last = cls.last_call.setdefault(_rate_domain, [Lock(), 0])
            with lock_last[0]:  # Obtain the domain specific lock
                cls.lock.release()
                # Sleep if necessary, then perform the request
                now = time.time()
                delay = lock_last[1] + _rate_delay - now
                if delay > 0:
                    now += delay
                    time.sleep(delay)
                lock_last[1] = now
                return function(cls, **kwargs)
        return wrapped

    def request(self, request, proxies, timeout, **_):
        """Responsible for dispatching the request and returning the result.

        Network level exceptions should be raised and only
        ``requests.Response`` should be returned.

        :param request: A ``requests.PreparedRequest`` object containing all
            the data necessary to perform the request.
        :param proxies: A dictionary of proxy settings to be utilized for the
            request.
        :param timeout: Specifies the maximum time that the actual HTTP request
            can take.

        ``**_`` should be added to the method call to ignore the extra
        arguments intended for the cache hander.

        """
        return self.http.send(request, proxies=proxies, timeout=timeout,
                              allow_redirects=False)
RateLimitHandler.request = RateLimitHandler.rate_limit(
    RateLimitHandler.request)


class DefaultHandler(RateLimitHandler):

    """Extends the RateLimitHandler to add thread-safe caching support."""

    # TODO: Actually make this thread safe
    cache = {}
    timeouts = {}

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
    def request(self, **kwargs):
        """Dispatch the request and return the result."""
        return super(DefaultHandler, self).request(**kwargs)


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

    def evict(self, urls):
        """We don't have a cache yet, so this does nothing."""

    def request(self, **kwargs):
        """Make the http request and return the http response."""
        return self._relay(method='request', **kwargs)
