"""Prepare py.test."""
import os
import socket
import time
from base64 import b64encode
from sys import platform

import betamax
from betamax_serializers import pretty_json


# Prevent calls to sleep
def _sleep(*args):
    raise Exception('Call to sleep')
time.sleep = _sleep


def b64_string(input_string):
    """Return a base64 encoded string (not bytes) from input_string."""
    return b64encode(input_string.encode('utf-8')).decode('utf-8')


def env_default(key):
    """Return environment variable or placeholder string."""
    return os.environ.get('prawtest_{}'.format(key),
                          'placeholder_{}'.format(key))


os.environ['praw_check_for_updates'] = 'False'


placeholders = {x: env_default(x) for x in
                ('auth_code client_id client_secret password redirect_uri '
                 'test_subreddit user_agent username').split()}
placeholders['basic_auth'] = b64_string(
    '{}:{}'.format(placeholders['client_id'], placeholders['client_secret']))


betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/integration/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    for key, value in placeholders.items():
        config.define_cassette_placeholder('<{}>'.format(key.upper()), value)


def pytest_namespace():
    """Add attributes to pytest in all tests."""
    return {'placeholders': placeholders}


if platform == 'darwin':  # Work around issue with betamax on OS X
    socket.gethostbyname = lambda x: '127.0.0.1'
