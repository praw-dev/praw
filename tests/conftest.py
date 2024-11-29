"""Prepare py.test."""

import os
import socket
import time
from base64 import b64encode
from sys import platform, modules
from urllib.parse import urlparse

import requests
import niquests
import urllib3

# betamax is tied to Requests
# and Niquests is almost entirely compatible with it.
# we can fool it without effort.
modules["requests"] = niquests
modules["requests.adapters"] = niquests.adapters
modules["requests.models"] = niquests.models
modules["requests.exceptions"] = niquests.exceptions
modules["requests.packages.urllib3"] = urllib3

# niquests no longer have a compat submodule
# but betamax need it. no worries, as betamax
# explicitly need requests, we'll give it to him.
modules["requests.compat"] = requests.compat

# doing the import now will make betamax working with Niquests!
# no extra effort.
import betamax

# the base mock does not implement close(), which is required
# for our HTTP client. No biggy.
betamax.mock_response.MockHTTPResponse.close = lambda _: None


# betamax have a tiny bug in URI matcher
# https://example.com != https://example.com/
# And Niquests does not enforce the trailing '/'
# when preparing a Request.
def _patched_parse(self, uri):
    parsed = urlparse(uri)
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path or "/",
        "fragment": parsed.fragment,
    }


betamax.matchers.uri.URIMatcher.parse = _patched_parse

import pytest


@pytest.fixture(autouse=True)
def patch_sleep(monkeypatch):
    """Auto patch sleep to speed up tests."""

    def _sleep(*_, **__):
        """Dud sleep function."""
        return

    monkeypatch.setattr(time, "sleep", value=_sleep)


@pytest.fixture
def image_path():
    """Return path to image."""

    def _get_path(name):
        """Return path to image."""
        return os.path.join(os.path.dirname(__file__), "integration", "files", name)

    return _get_path


@pytest.fixture(autouse=True)
def lax_content_length_strict(monkeypatch):
    import io
    import base64
    from betamax.util import body_io
    from urllib3 import HTTPResponse
    from betamax.mock_response import MockHTTPResponse

    # our cassettes are[...] pretty much broken.
    # Some declared Content-Length don't match the bodies.
    # Let's disable enforced content-length here.
    def _patched_add_urllib3_response(serialized, response, headers):
        if "base64_string" in serialized["body"]:
            body = io.BytesIO(
                base64.b64decode(serialized["body"]["base64_string"].encode())
            )
        else:
            body = body_io(**serialized["body"])

        h = HTTPResponse(
            body,
            status=response.status_code,
            reason=response.reason,
            headers=headers,
            preload_content=False,
            original_response=MockHTTPResponse(headers),
            enforce_content_length=False,
        )

        response.raw = h

    monkeypatch.setattr(
        betamax.util, "add_urllib3_response", _patched_add_urllib3_response
    )


def pytest_configure(config):
    pytest.placeholders = Placeholders(placeholders)
    config.addinivalue_line(
        "markers", "add_placeholder: Define an additional placeholder for the cassette."
    )
    config.addinivalue_line(
        "markers", "cassette_name: Name of cassette to use for test."
    )
    config.addinivalue_line(
        "markers", "recorder_kwargs: Arguments to pass to the recorder."
    )


os.environ["praw_check_for_updates"] = "False"


placeholders = {
    x: os.environ.get(f"prawtest_{x}", f"placeholder_{x}")
    for x in (
        "auth_code client_id client_secret password redirect_uri test_subreddit"
        " user_agent username refresh_token"
    ).split()
}


placeholders["basic_auth"] = b64encode(
    f"{placeholders['client_id']}:{placeholders['client_secret']}".encode("utf-8")
).decode("utf-8")


class Placeholders:
    def __init__(self, _dict):
        self.__dict__ = _dict


if platform == "darwin":  # Work around issue with betamax on OS X
    socket.gethostbyname = lambda x: "127.0.0.1"
