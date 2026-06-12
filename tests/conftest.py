"""Prepare py.test."""

import os
import time
from base64 import b64encode
from urllib.parse import quote_plus

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


def pytest_configure(config):
    pytest.placeholders = Placeholders(placeholders)
    config.addinivalue_line("markers", "add_placeholder: Define an additional placeholder for the cassette.")
    config.addinivalue_line("markers", "cassette_name: Name of cassette to use for test.")
    config.addinivalue_line("markers", "recorder_kwargs: Arguments to pass to the recorder.")


os.environ["praw_check_for_updates"] = "False"


placeholders = {
    x: os.environ.get(f"prawtest_{x}", f"placeholder_{x}")
    for x in [
        "auth_code",
        "client_id",
        "client_secret",
        "password",
        "redirect_uri",
        "test_subreddit",
        "user_agent",
        "username",
        "refresh_token",
    ]
}


placeholders["basic_auth"] = b64encode(f"{placeholders['client_id']}:{placeholders['client_secret']}".encode()).decode(
    "utf-8"
)


# Values the cassette persister substitutes to/from ``<PLACEHOLDER>`` tokens on disk. The
# password is URL-encoded because that is the form in which it appears in request bodies.
cassette_placeholders = {**placeholders, "password": quote_plus(placeholders["password"])}


class Placeholders:
    def __init__(self, _dict):
        self.__dict__ = _dict
