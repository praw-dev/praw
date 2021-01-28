"""Test classes from collections.py."""
import pytest

from praw.models import Collection
from praw.models.reddit.collections import SubredditCollections

from ... import UnitTest


class TestCollection(UnitTest):
    def test_eq(self):
        uuid = "fake_uuid"
        permalink = f"https://reddit.com/r/subreddit/collection/{uuid}"
        collection1 = Collection(self.reddit, collection_id=uuid)
        collection2 = Collection(self.reddit, permalink=permalink)
        assert collection1 == collection2
        assert collection2 == collection2
        assert collection1 == collection1
        assert uuid == collection1
        assert uuid == collection2

    def test_init(self):
        uuid = "fake_uuid"
        assert uuid == Collection(self.reddit, collection_id=uuid).collection_id
        permalink = f"https://reddit.com/r/subreddit/collection/{uuid}"
        assert uuid == Collection(self.reddit, permalink=permalink).collection_id

    def test_init_bad(self):
        with pytest.raises(TypeError):
            Collection(self.reddit)
        with pytest.raises(TypeError):
            Collection(self.reddit, _data=dict(), collection_id="")
        with pytest.raises(TypeError):
            Collection(self.reddit, collection_id="fake_uuid", permalink="")
        with pytest.raises(TypeError):
            Collection(
                None,
                _data={"collection_id": "fake_uuid"},
                collection_id="fake_uuid",
                permalink="https://reddit.com/r/sub/collection/fake_uuid",
            )
        with pytest.raises(ValueError):
            Collection(self.reddit, collection_id="")
        with pytest.raises(ValueError):
            Collection(self.reddit, permalink="")

    def test_repr(self):
        collection = Collection(self.reddit, collection_id="fake_uuid")
        assert "Collection(collection_id='fake_uuid')" == repr(collection)

    def test_str(self):
        collection = Collection(self.reddit, collection_id="fake_uuid")
        assert "fake_uuid" == str(collection)

    def test_neq(self):
        collection1 = Collection(self.reddit, collection_id="1")
        collection2 = Collection(self.reddit, collection_id="2")
        assert collection1 != collection2
        assert "1" != collection2
        assert "2" != collection1


class TestSubredditCollections(UnitTest):
    def test_call(self):
        collections = SubredditCollections(
            self.reddit, self.reddit.subreddit("placeholder")
        )
        with pytest.raises(TypeError):
            collections()
        with pytest.raises(TypeError):
            collections("a uuid", "a permalink")
