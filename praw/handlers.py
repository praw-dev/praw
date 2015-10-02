# coding=ascii
"""Provides classes that handle request dispatching."""
import sys
import socket
import time
from logging import getLogger
from requests import Session
from threading import Lock
from praw.helpers import normalize_url
from praw.errors import ClientException
from functools import wraps
from six.moves import cPickle


class RateLimitHandler(object):
    """The base handler that provides thread-safe rate limiting enforcement.
    While this handler is threadsafe, PRAW is not thread safe when the same
    `Reddit` instance is being utilized from multiple threads.
    """

    def __init__(self):
        self.logger = getLogger('hndl')
        self.no_auth = time.time() - 1                              # simply the time since the last no_auth was sent
        self.oauth = {}                                             # {'unique request token': [last_sent, lifetime]}
        self.http = Session()
        self.rl_lock = Lock()

    # noinspection PyBroadException
    def __del__(self):
        """
        Cleans up the http session on object deletion
        """
        if self.http:
            try:
                self.http.close()
            except Exception:
                pass

    # noinspection PyUnusedLocal
    @classmethod
    def evict(cls, urls):
        """Method utilized to evict entries for the given urls.
        :param urls: An iterable containing normalized urls.
        :returns: Whether or not an item was removed from the cache.
        By default this method returns False as a cache need not be present.
        """
        return False

    def request(self, request, proxies, timeout, verify, **_):
        """
        Cleans up the ``oauth`` attribute, then looks up if its an OAuth requests and dispatched the request in the
        appropriate time. Sleeps the thread for exactly the time until the next request can be sent.

        :param request: A ``requests.PreparedRequest`` object containing all the data necessary to perform the request.
        :param proxies: A dictionary of proxy settings to be utilized for the request.
        :param timeout: Specifies the maximum time that the actual HTTP request can take.
        :param verify: Specifies if SSL certificates should be validated.
        """
        # cleans up the dictionary with access keys every time someone tries a request.
        self.oauth = {key: value for key, value in self.oauth.items() if value[1] > time.time()}
        bearer = ''
        if '_cache_key' in _:
            cache_key = _.get('_cache_key')
            token_group = cache_key[1]
            if len(token_group) >= 5:
                bearer = token_group[4]

        if bearer and bearer in self.oauth:
            if bearer in self.oauth:
                # lock the thread to update values
                self.rl_lock.acquire()
                last_dispatched = self.oauth[bearer][0]
                left_until_dispatch = self.dispatch_timer(last_dispatched + 1)
                self.oauth[bearer][0] = time.time() + left_until_dispatch
                self.rl_lock.release()
                # and now we can sleep the single thread in here - the timer should've updated, so the next
                # thread cannot possibly dispatch at the same time, instead gets slept later in.
                time.sleep(left_until_dispatch)
        elif bearer:
            self.oauth[bearer] = [time.time(), time.time() + 70 * 60]  # lifetime: 70 minutes
        else:
            self.rl_lock.acquire()
            last_dispatched = self.no_auth
            left_until_dispatch = self.dispatch_timer(last_dispatched + 2)
            self.no_auth = time.time() + left_until_dispatch
            self.rl_lock.release()
            time.sleep(left_until_dispatch)
        return self.send_request(request, proxies, timeout, verify)

    def send_request(self, request, proxies, timeout, verify):
        """
        Responsible for dispatching the request and returning the result.
        Network level exceptions should be raised and only ``requests.Response`` should be returned.

        ``**_`` should be added to the method call to ignore the extra arguments intended for the cache handler.

        :param request: A ``requests.PreparedRequest`` object containing all the data necessary to perform the request.
        :param proxies: A dictionary of proxy settings to be utilized for the request.
        :param timeout: Specifies the maximum time that the actual HTTP request can take.
        :param verify: Specifies if SSL certificates should be validated.
        """
        self.logger.debug('{:4} {}'.format(request.method, request.url))
        return self.http.send(request, proxies=proxies, timeout=timeout, allow_redirects=False, verify=verify)

    @staticmethod
    def dispatch_timer(next_possible_dispatch):
        """
        Method to determine when the next request can be dispatched.
        :param next_possible_dispatch: Timestamp of the next possible dispatch.
        :type next_possible_dispatch: int | float
        :return: int | float
        """
        time_until_dispatch = next_possible_dispatch - time.time()
        if time_until_dispatch > 0:  # Make sure that we have given it enough time.
            return time_until_dispatch
        return 0


class DefaultHandler(RateLimitHandler):

    """Extends the RateLimitHandler to add thread-safe caching support."""

    ca_lock = Lock()
    cache = {}
    cache_hit_callback = None
    timeouts = {}

    @staticmethod
    def with_cache(function):
        """Return a decorator that interacts with a handler's cache.
        This decorator must be applied to a DefaultHandler class method or
        instance method as it assumes `cache`, `ca_lock` and `timeouts` are
        available.
        """
        @wraps(function)
        def wrapped(cls, _cache_key, _cache_ignore, _cache_timeout, **kwargs):
            def clear_timeouts():
                """Clear the cache of timed out results."""
                for key in list(cls.timeouts):
                    if time.time() - cls.timeouts[key] > _cache_timeout:
                        del cls.timeouts[key]
                        del cls.cache[key]

            if _cache_ignore:
                return function(cls, **kwargs)
            with cls.ca_lock:
                clear_timeouts()
                if _cache_key in cls.cache:
                    if cls.cache_hit_callback:
                        cls.cache_hit_callback(_cache_key)
                    return cls.cache[_cache_key]
            # Releasing the lock before actually making the request allows for
            # the possibility of more than one thread making the same request
            # to get through. Without having domain-specific caching (under the
            # assumption only one request to a domain can be made at a
            # time), there isn't a better way to handle this.
            result = function(cls, **kwargs)
            # The handlers don't call `raise_for_status` so we need to ignore
            # status codes that will result in an exception that should not be
            # cached.
            if result.status_code not in (200, 302):
                return result
            with cls.ca_lock:
                cls.timeouts[_cache_key] = time.time()
                cls.cache[_cache_key] = result
                return result
        return wrapped

    @classmethod
    def evict(cls, urls):
        """Remove items from cache matching URL.
        Return whether or not any items were removed.
        """
        urls = set(normalize_url(url) for url in urls)
        retval = False
        with cls.ca_lock:
            for key in list(cls.cache):
                if key[0] in urls:
                    retval = True
                    del cls.cache[key]
                    del cls.timeouts[key]
        return retval
DefaultHandler.request = DefaultHandler.with_cache(RateLimitHandler.request)


class MultiprocessHandler(object):

    """A PRAW handler to interact with the PRAW multi-process server."""

    def __init__(self, host='localhost', port=10101):
        self.host = host
        self.port = port

    def _relay(self, **kwargs):
        """Send the request through the Server and return the http response."""
        retval = None
        delay_time = 2  # For connection retries
        read_attempts = 0  # For reading from socket
        while retval is None:  # Evict can return False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_fp = sock.makefile('rwb')  # Used for pickle
            try:
                sock.connect((self.host, self.port))
                cPickle.dump(kwargs, sock_fp, cPickle.HIGHEST_PROTOCOL)
                sock_fp.flush()
                retval = cPickle.load(sock_fp)
            except:  # pylint: disable-msg=W0702
                exc_type, exc, _ = sys.exc_info()
                socket_error = exc_type is socket.error
                if socket_error and exc.errno == 111:  # Connection refused
                    sys.stderr.write('Cannot connect to multiprocess server. I'
                                     's it running? Retrying in {0} seconds.\n'
                                     .format(delay_time))
                    time.sleep(delay_time)
                    delay_time = min(64, delay_time * 2)
                elif exc_type is EOFError or socket_error and exc.errno == 104:
                    # Failure during socket READ
                    if read_attempts >= 3:
                        raise ClientException('Successive failures reading '
                                              'from the multiprocess server.')
                    sys.stderr.write('Lost connection with multiprocess server'
                                     ' during read. Trying again.\n')
                    read_attempts += 1
                else:
                    raise
            finally:
                sock_fp.close()
                sock.close()
        if isinstance(retval, Exception):
            raise retval  # pylint: disable-msg=E0702
        return retval

    def evict(self, urls):
        """Forward the eviction to the server and return its response."""
        return self._relay(method='evict', urls=urls)

    def request(self, **kwargs):
        """Forward the request to the server and return its http response."""
        return self._relay(method='request', **kwargs)
