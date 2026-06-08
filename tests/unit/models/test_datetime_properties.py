from datetime import datetime

import pytest

from praw.models import Collection, Comment, Submission
from praw.models.mod_note import ModNote
from praw.models.reddit.poll import PollData

from .. import UnitTest


class TestCreatedDatetime(UnitTest):
    def test_created_datetime__from_created_at(self, reddit):
        note = ModNote(reddit, _data={"id": "n", "created_at": 1648167599})
        assert note.created_datetime.tzinfo is not None
        assert note.created_datetime.timestamp() == 1648167599

    def test_created_datetime__from_created_at_utc(self, reddit):
        collection = Collection(
            reddit,
            _data={"collection_id": "u", "created_at_utc": 1588137147.0, "last_update_utc": 1588200000.0},
        )
        assert collection.created_datetime.tzinfo is not None
        assert collection.created_datetime.timestamp() == 1588137147.0

    def test_created_datetime__from_created_utc(self, reddit):
        comment = Comment(reddit, _data={"id": "abc", "created_utc": 1588137147.0})
        assert isinstance(comment.created_datetime, datetime)
        assert comment.created_datetime.tzinfo is not None
        assert comment.created_datetime.timestamp() == 1588137147.0


class TestEditedDatetime(UnitTest):
    def test_edited_datetime__never_edited(self, reddit):
        comment = Comment(reddit, _data={"id": "abc", "edited": False})
        assert comment.edited_datetime is None

    def test_edited_datetime__when_edited(self, reddit):
        submission = Submission(reddit, _data={"id": "abc", "edited": 1341972591.0})
        assert submission.edited_datetime.tzinfo is not None
        assert submission.edited_datetime.timestamp() == 1341972591.0


class TestUpdatedDatetime(UnitTest):
    def test_updated_datetime(self, reddit):
        collection = Collection(
            reddit,
            _data={"collection_id": "u", "created_at_utc": 1588137147.0, "last_update_utc": 1588200000.0},
        )
        assert collection.updated_datetime.tzinfo is not None
        assert collection.updated_datetime.timestamp() == 1588200000.0


class TestVotingEndDatetime(UnitTest):
    def test_voting_end_datetime__converts_milliseconds(self, reddit):
        poll_data = PollData(reddit, _data={"voting_end_timestamp": 1588309947690})
        assert poll_data.voting_end_datetime.tzinfo is not None
        assert poll_data.voting_end_datetime.timestamp() == pytest.approx(1588309947.69)
