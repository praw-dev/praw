"""Prepare pytest for unit tests."""

import pytest

from praw import Reddit


@pytest.fixture
def reddit():
    """Return an instance of :class:`.Reddit` that doesn't make requests to Reddit."""
    reddit = Reddit(client_id="dummy", client_secret="dummy", user_agent="dummy")
    # Unit tests should never issue requests
    reddit._core.request = dummy_request
    yield reddit


def dummy_request(*args, **kwargs):
    pass
