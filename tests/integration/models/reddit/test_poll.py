"""Test praw.models.poll."""

import pytest

from praw.models import PollData, PollOption

from ... import IntegrationTest


class TestPollData(IntegrationTest):
    def test_get_attrs(self, reddit):
        poll_id = "fo7p5b"
        submission = reddit.submission(poll_id)
        poll_data = submission.poll_data
        assert isinstance(poll_data, PollData)
        assert isinstance(poll_data.options, list)
        assert all(isinstance(option, PollOption) for option in poll_data.options)
        assert poll_data.user_selection is None  # not logged in

        with pytest.raises(KeyError):
            poll_data.option("badID")

    def test_get_user_selection(self, reddit):
        poll_id = "g9zfex"
        reddit.read_only = False
        submission = reddit.submission(poll_id)
        poll_data = submission.poll_data
        # For this test to pass, the authenticated user should have
        # voted in the poll specified.
        assert isinstance(poll_data.user_selection, PollOption)
