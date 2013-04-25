"""Provides a request server to be used with the multiprocess handler."""

import socket
import sys
from praw.handlers import DefaultHandler
from requests import Session
from six.moves import cPickle, socketserver
from threading import Lock


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # pylint: disable-msg=R0903,W0232

    """A TCP server that creates new threads per connection."""

    allow_reuse_address = True

    @staticmethod
    def handle_error(_, client_addr):
        """Mute tracebacks of common errors."""
        exc_type, exc_value, _ = sys.exc_info()
        if exc_type is socket.error and exc_value[0] == 32:
            pass
        elif exc_type is cPickle.UnpicklingError:
            sys.stdout.write('Invalid connection from {0}\n'
                             .format(client_addr[0]))
        else:
            raise


class RequestHandler(socketserver.StreamRequestHandler):
    # pylint: disable-msg=W0232

    """A class that handles incoming requests.

    Requests to the same domain are cached and rate-limited.

    """

    ca_lock = Lock()  # lock around cache and timeouts
    cache = {}  # caches requests
    http = Session()  # used to make requests
    last_call = {}  # Stores a two-item list: [lock, previous_call_time]
    rl_lock = Lock()  # lock used for adding items to last_call
    timeouts = {}  # store the time items in cache were entered

    @staticmethod
    def cache_hit_callback(key):
        """Output when a cache hit occurs."""
        print('HIT {0} {1}'.format('POST' if key[1][1] else 'GET', key[0]))

    @DefaultHandler.with_cache
    @DefaultHandler.rate_limit
    def do_request(self, request, proxies, timeout, **_):
        """Dispatch the actual request and return the result."""
        print('{0} {1}'.format(request.method, request.url))
        response = self.http.send(request, proxies=proxies, timeout=timeout,
                                  allow_redirects=False)
        response.raw = None  # Make pickleable
        return response

    def handle(self):
        """Parse the RPC, make the call, and pickle up the return value."""
        data = cPickle.load(self.rfile)  # pylint: disable-msg=E1101
        method = data.pop('method')
        try:
            retval = getattr(self, 'do_{0}'.format(method))(**data)
        except Exception as exc:
            # All exceptions should be passed to the client
            # TODO: "Fix" some exceptions that aren't pickle-able
            retval = exc
        cPickle.dump(retval, self.wfile,  # pylint: disable-msg=E1101
                     cPickle.HIGHEST_PROTOCOL)
RequestHandler.do_evict = DefaultHandler.evict


def run():
    """The entry point from the praw-multiprocess utility."""
    host = 'localhost'
    port = 10101
    server = ThreadingTCPServer((host, port), RequestHandler)
    print('Listening on {0} port {1}'.format(host, port))
    server.serve_forever()  # pylint: disable-msg=E1101
