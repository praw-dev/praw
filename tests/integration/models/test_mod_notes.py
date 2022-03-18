from unittest import mock

import pytest

from .. import IntegrationTest


class TestModNotes(IntegrationTest):
    REDDITOR = "pyapitestuser3"

    def test_create_note__submission(self):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = self.reddit.submission("uflrmv")
            result_note = submission.mod.create_note(
                label="HELPFUL_USER", note="test note"
            )
            assert result_note.user == submission.author
            assert result_note.note == "test note"
            assert result_note.label == "HELPFUL_USER"

    def test_create_note__thing_fullname(self):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = self.reddit.submission("uflrmv")
            result_note = self.reddit.notes.create(
                label="HELPFUL_USER", note="test note", thing=submission.fullname
            )
            assert result_note.user == submission.author
            assert result_note.id.startswith("ModNote")
            assert result_note.moderator.name == pytest.placeholders.username
            assert result_note.note == "test note"
            assert result_note.label == "HELPFUL_USER"
            assert result_note.reddit_id == submission.fullname

    def test_create_note__thing_submission(self):
        self.reddit.read_only = False
        with self.use_cassette("TestModNotes.test_create_note__submission"):
            submission = self.reddit.submission("uflrmv")
            result_note = self.reddit.notes.create(
                label="HELPFUL_USER", note="test note", thing=submission
            )
            assert result_note.user == submission.author
            assert result_note.note == "test note"

    @mock.patch("time.sleep", return_value=None)
    def test_delete_note(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            result_note = subreddit.mod.notes.create(
                redditor=self.REDDITOR, note="test note"
            )
            subreddit.mod.notes.delete(
                note_id=result_note.id, redditor=result_note.user
            )
            notes = list(subreddit.mod.notes.redditors(self.REDDITOR))
            assert result_note not in notes

    @mock.patch("time.sleep", return_value=None)
    def test_delete_note__all_notes(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            result_note = subreddit.mod.notes.create(
                redditor=self.REDDITOR, note="test note"
            )
            subreddit.mod.notes.delete(delete_all=True, redditor=result_note.user)
            notes = list(subreddit.mod.notes.redditors(self.REDDITOR))
            assert len(notes) == 0
