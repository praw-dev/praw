"""A test that is run only by Github Actions

This test makes real network requests, so environment variables
should be specified in Github Actions.
"""
import os

import pytest

from praw import Reddit
from praw.models import Submission


@pytest.mark.skipif(
    not os.getenv("NETWORK_TEST_CLIENT_ID"),
    reason="Not running from the NETWORK_TEST ci task on praw-dev/praw",
)
def test_github_actions():
    reddit = Reddit(
        client_id=os.getenv("NETWORK_TEST_CLIENT_ID"),
        client_secret=os.getenv("NETWORK_TEST_CLIENT_SECRET"),
        user_agent="Github Actions CI Testing",
    )
    assert isinstance(next(reddit.subreddit("all").hot()), Submission)
