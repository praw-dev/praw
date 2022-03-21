import pickle

import pytest

from praw.models import Draft, Subreddit

from ... import UnitTest


class TestDraft(UnitTest):
    def test_construct_failure(self):
        message = "Exactly one of `id` or `_data` must be provided."
        with pytest.raises(TypeError) as excinfo:
            Draft(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Draft(self.reddit, "dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Draft(self.reddit, id="dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

    def test_create_failure(self):
        with pytest.raises(TypeError) as excinfo:
            self.reddit.drafts.create(url="url", selftext="selftext")
        assert (
            str(excinfo.value) == "Exactly one of `selftext` or `url` must be provided."
        )

    def test_equality(self):
        draft1 = Draft(self.reddit, _data={"id": "dummy1"})
        draft2 = Draft(self.reddit, _data={"id": "dummy1"})
        draft3 = Draft(self.reddit, _data={"id": "dummy3"})
        assert draft1 == draft1
        assert draft2 == draft2
        assert draft3 == draft3
        assert draft1 == draft2
        assert draft2 != draft3
        assert draft1 != draft3
        assert "dummy1" == draft1
        assert draft2 == "dummy1"

        draft1 = Draft(
            self.reddit, _data={"id": "dummy1", "body": "body1", "kind": "markdown"}
        )
        draft2 = Draft(
            self.reddit, _data={"id": "dummy1", "body": "body1", "kind": "markdown"}
        )
        draft3 = Draft(
            self.reddit, _data={"id": "dummy3", "body": "body2", "kind": "markdown"}
        )
        assert draft1 == draft1
        assert draft2 == draft2
        assert draft3 == draft3
        assert draft1 == draft2
        assert draft2 != draft3
        assert draft1 != draft3

        draft1 = Draft(
            self.reddit, _data={"id": "dummy1", "body": "url1", "kind": "link"}
        )
        draft2 = Draft(
            self.reddit, _data={"id": "dummy1", "body": "url1", "kind": "link"}
        )
        draft3 = Draft(
            self.reddit, _data={"id": "dummy3", "body": "url3", "kind": "link"}
        )
        assert draft1 == draft1
        assert draft2 == draft2
        assert draft3 == draft3
        assert draft1 == draft2
        assert draft2 != draft3
        assert draft1 != draft3

    def test_hash(self):
        draft1 = Draft(
            self.reddit, _data={"id": "dummy1", "body": "body1", "kind": "markdown"}
        )
        draft2 = Draft(
            self.reddit, _data={"id": "dummy1", "body": "body2", "kind": "markdown"}
        )
        draft3 = Draft(
            self.reddit, _data={"id": "dummy3", "body": "body2", "kind": "markdown"}
        )
        assert hash(draft1) == hash(draft1)
        assert hash(draft2) == hash(draft2)
        assert hash(draft3) == hash(draft3)
        assert hash(draft1) == hash(draft2)
        assert hash(draft2) != hash(draft3)
        assert hash(draft1) != hash(draft3)

    def test_pickle(self):
        draft = Draft(self.reddit, _data={"id": "dummy"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(draft, protocol=level))
            assert draft == other

    def test_repr(self):
        draft = Draft(self.reddit, id="draft_id")
        assert repr(draft) == "Draft(id='draft_id')"

        data = {"id": "draft_id", "body": "body", "kind": "markdown"}
        subreddit = Subreddit(None, "subreddit")
        draft = Draft(
            self.reddit, _data={**data, "subreddit": subreddit, "title": None}
        )
        assert repr(draft) == "Draft(id='draft_id' subreddit='subreddit')"

        draft = Draft(self.reddit, _data={**data, "subreddit": None, "title": "title"})
        assert repr(draft) == "Draft(id='draft_id' title='title')"

        draft = Draft(
            self.reddit, _data={**data, "subreddit": subreddit, "title": "title"}
        )
        assert repr(draft) == "Draft(id='draft_id' subreddit='subreddit' title='title')"

    def test_str(self):
        draft = Draft(self.reddit, _data={"id": "dummy"})
        assert str(draft) == "dummy"

    def test_submit_failure(self):
        draft = Draft(
            self.reddit,
            _data={
                "id": "draft_id",
                "body": "body",
                "kind": "markdown",
                "subreddit": None,
            },
        )
        with pytest.raises(ValueError) as excinfo:
            draft.submit()
            assert (
                str(excinfo.value)
                == "`subreddit` must be set on the Draft or passed as a keyword argument."
            )
