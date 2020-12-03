"""Test classes from collections.py."""

from unittest import mock

import pytest

from praw.exceptions import ClientException
from praw.models import Submission

from ... import IntegrationTest


class TestCollection(IntegrationTest):
    NONEMPTY_REAL_UUID = "847e4548-a3b5-4ad7-afb4-edbfc2ed0a6b"

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_bad_fetch(self):
        uuid = "A" * 36
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            with pytest.raises(ClientException):
                collection._fetch()

    def test_init(self):
        uuid = self.NONEMPTY_REAL_UUID
        with self.use_cassette():
            collection1 = self.subreddit.collections(uuid)
            collection2 = self.subreddit.collections(permalink=collection1.permalink)
            assert collection1 == collection2

    def test_iter(self):
        uuid = self.NONEMPTY_REAL_UUID
        found_some = False
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            for post in collection:
                assert isinstance(post, Submission)
                found_some = True
        assert found_some

    def test_follow(self):
        self.reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            collection.follow()

    def test_subreddit(self):
        uuid = self.NONEMPTY_REAL_UUID
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            assert str(collection.subreddit) in collection.permalink

    def test_unfollow(self):
        self.reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            collection.unfollow()


class TestCollectionModeration(IntegrationTest):
    NONEMPTY_REAL_UUID = "847e4548-a3b5-4ad7-afb4-edbfc2ed0a6b"

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test_add_post(self, _):
        self.reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            posts = [self.subreddit.submit(f"Post #{i}", selftext="") for i in range(4)]

            # Testing different types for _post_fullname
            collection.mod.add_post(posts[0])  # Subreddit object
            collection.mod.add_post(posts[1].fullname)  # fullname
            collection.mod.add_post(f"https://reddit.com{posts[2].permalink}")
            collection.mod.add_post(posts[3].id)  # id

            posts.append(
                self.subreddit.submit("Post #4", selftext="", collection_id=uuid)
            )

            with pytest.raises(TypeError):
                collection.mod.add_post(12345)

            collection._fetch()

            collection_set = set(collection)
            for post in posts:
                assert post in collection_set

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            collection = self.subreddit.collections.mod.create("Title", "")
            collection.mod.delete()

    @mock.patch("time.sleep", return_value=None)
    def test_remove_post(self, _):
        self.reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        with self.use_cassette():
            post = self.subreddit.submit("The title", selftext="", collection_id=uuid)
            collection = self.subreddit.collections(uuid)
            collection.mod.remove_post(post)

    @mock.patch("time.sleep", return_value=None)
    def test_reorder(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            collection = self.subreddit.collections(self.NONEMPTY_REAL_UUID)
            original_order = collection.link_ids
            new_order = (
                collection.link_ids[len(collection.link_ids) // 2 :]
                + collection.link_ids[: len(collection.link_ids) // 2]
            )
            assert len(original_order) == len(new_order)
            assert original_order != new_order
            collection.mod.reorder(new_order)
            collection._fetch()
            assert collection.link_ids == new_order

    @mock.patch("time.sleep", return_value=None)
    def test_update_description(self, _):
        self.reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        new_description = "b" * 250
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            collection.mod.update_description(new_description)
            assert new_description == collection.description

    @mock.patch("time.sleep", return_value=None)
    def test_update_title(self, _):
        self.reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        new_title = "a" * 100
        with self.use_cassette():
            collection = self.subreddit.collections(uuid)
            collection.mod.update_title(new_title)
            assert new_title == collection.title


class TestSubredditCollections(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test_call(self, _):
        with self.use_cassette():
            collection = next(iter(self.subreddit.collections))
            assert collection == self.subreddit.collections(collection.collection_id)
            assert collection == self.subreddit.collections(
                permalink=collection.permalink
            )

    @mock.patch("time.sleep", return_value=None)
    def test_iter(self, _):
        with self.use_cassette():
            found_any = False
            for collection in self.subreddit.collections:
                assert collection.permalink
                assert collection.title is not None
                assert collection.description is not None
                found_any = True
            assert found_any


class TestSubredditCollectionsModeration(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test_create(self, _):
        title = "The title!"
        description = "The description."
        self.reddit.read_only = False
        with self.use_cassette():
            collection = self.subreddit.collections.mod.create(title, description)
            assert collection.title == title
            assert collection.description == description
            assert len(collection) == 0
