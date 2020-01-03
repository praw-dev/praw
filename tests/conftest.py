"""Prepare py.test."""
from base64 import b64encode
from functools import wraps
import json
import os
import socket
import sys
from sys import platform
import time

import betamax
from betamax.cassette.cassette import dispatch_hooks, Cassette
import pytest
from betamax_serializers import pretty_json


# pylint: disable=import-error,no-name-in-module
if sys.version_info.major == 2:
    from urllib import quote_plus  # NOQA
else:
    from urllib.parse import quote_plus  # NOQA


# Prevent calls to sleep
def _sleep(*args):
    raise Exception("Call to sleep")


time.sleep = _sleep


def b64_string(input_string):
    """Return a base64 encoded string (not bytes) from input_string."""
    return b64encode(input_string.encode("utf-8")).decode("utf-8")


def env_default(key):
    """Return environment variable or placeholder string."""
    return os.environ.get(
        "prawtest_{}".format(key), "placeholder_{}".format(key)
    )


def filter_access_token(interaction, current_cassette):
    """Add Betamax placeholder to filter access token."""
    request_uri = interaction.data["request"]["uri"]
    response = interaction.data["response"]
    if (
        "api/v1/access_token" not in request_uri
        or response["status"]["code"] != 200
    ):
        return
    body = response["body"]["string"]
    try:
        token = json.loads(body)["access_token"]
    except (KeyError, TypeError, ValueError):
        return
    current_cassette.placeholders.append(
        betamax.cassette.cassette.Placeholder(
            placeholder="<ACCESS_TOKEN>", replace=token
        )
    )


os.environ["praw_check_for_updates"] = "False"


placeholders = {
    x: env_default(x)
    for x in (
        "auth_code client_id client_secret password redirect_uri "
        "test_subreddit user_agent username refresh_token"
    ).split()
}


placeholders["basic_auth"] = b64_string(
    "{}:{}".format(placeholders["client_id"], placeholders["client_secret"])
)


betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with betamax.Betamax.configure() as config:
    config.cassette_library_dir = "tests/integration/cassettes"
    config.default_cassette_options["serialize_with"] = "prettyjson"
    config.before_record(callback=filter_access_token)
    for key, value in placeholders.items():
        if key == "password":
            value = quote_plus(value)
        config.define_cassette_placeholder("<{}>".format(key.upper()), value)


def add_init_hook(original_init):
    """Wrap an __init__ method to also call some hooks."""

    @wraps(original_init)
    def wrapper(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        dispatch_hooks("after_init", self)

    return wrapper


Cassette.__init__ = add_init_hook(Cassette.__init__)


def init_hook(cassette):
    if cassette.is_recording():
        pytest.set_up_record()  # dynamically defined in __init__.py


Cassette.hooks["after_init"].append(init_hook)


class Placeholders:
    def __init__(self, _dict):
        self.__dict__ = _dict


def pytest_configure():
    pytest.placeholders = Placeholders(placeholders)


if platform == "darwin":  # Work around issue with betamax on OS X
    socket.gethostbyname = lambda x: "127.0.0.1"
