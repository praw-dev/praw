"""Test classes from collections.py."""

import pytest

from praw.exceptions import ClientException, RedditAPIException
from praw.models import Submission

from ... import IntegrationTest


class TestCollection(IntegrationTest):
    NONEMPTY_REAL_UUID = "847e4548-a3b5-4ad7-afb4-edbfc2ed0a6b"

    def test_bad_fetch(self, reddit):
        uuid = "A" * 36
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        with pytest.raises(ClientException):
            collection._fetch()

    def test_follow(self, reddit):
        reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.follow()

    def test_init(self, reddit):
        uuid = self.NONEMPTY_REAL_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection1 = subreddit.collections(uuid)
        collection2 = subreddit.collections(permalink=collection1.permalink)
        assert collection1 == collection2

    def test_iter(self, reddit):
        uuid = self.NONEMPTY_REAL_UUID
        found_some = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        for post in collection:
            assert isinstance(post, Submission)
            found_some = True
        assert found_some

    def test_subreddit(self, reddit):
        uuid = self.NONEMPTY_REAL_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        assert str(collection.subreddit) in collection.permalink

    def test_unfollow(self, reddit):
        reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.unfollow()


class TestCollectionModeration(IntegrationTest):
    NONEMPTY_REAL_UUID = "847e4548-a3b5-4ad7-afb4-edbfc2ed0a6b"
    UPDATE_LAYOUT_UUID = "accd53cf-6f76-49fd-8ca5-5ad2036b4693"

    def test_add_post(self, reddit):
        reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        posts = [subreddit.submit(f"Post #{i}", selftext="") for i in range(4)]

        # Testing different types for _post_fullname
        collection.mod.add_post(posts[0])  # Subreddit object
        collection.mod.add_post(posts[1].fullname)  # fullname
        collection.mod.add_post(f"https://reddit.com{posts[2].permalink}")
        collection.mod.add_post(posts[3].id)  # id

        posts.append(subreddit.submit("Post #4", collection_id=uuid, selftext=""))

        with pytest.raises(TypeError):
            collection.mod.add_post(12345)

        collection._fetch()

        collection_set = set(collection)
        for post in posts:
            assert post in collection_set

    def test_delete(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections.mod.create(title="Title", description="")
        collection.mod.delete()

    def test_remove_post(self, reddit):
        reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        post = subreddit.submit("The title", collection_id=uuid, selftext="")
        collection = subreddit.collections(uuid)
        collection.mod.remove_post(post)

    def test_reorder(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(self.NONEMPTY_REAL_UUID)
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

    def test_update_description(self, reddit):
        reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        new_description = "b" * 250
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.mod.update_description(new_description)
        assert new_description == collection.description

    def test_update_display_layout__empty_string(self, reddit):
        reddit.read_only = False
        uuid = self.UPDATE_LAYOUT_UUID
        empty_string = ""
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.mod.update_display_layout(empty_string)
        assert empty_string != collection.display_layout
        assert collection.display_layout is None

    def test_update_display_layout__gallery(self, reddit):
        reddit.read_only = False
        uuid = self.UPDATE_LAYOUT_UUID
        gallery_layout = "GALLERY"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.mod.update_display_layout(gallery_layout)
        assert gallery_layout == collection.display_layout

    def test_update_display_layout__invalid_layout(self, reddit):
        reddit.read_only = False
        uuid = self.UPDATE_LAYOUT_UUID
        invalid_layout = "colossal atom cake"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        with pytest.raises(RedditAPIException):
            collection.mod.update_display_layout(invalid_layout)
        assert collection.display_layout is None

    def test_update_display_layout__lowercase(self, reddit):
        reddit.read_only = False
        uuid = self.UPDATE_LAYOUT_UUID
        lowercase_gallery_layout = "gallery"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        with pytest.raises(RedditAPIException):
            collection.mod.update_display_layout(lowercase_gallery_layout)
        assert collection.display_layout is None

    def test_update_display_layout__none(self, reddit):
        reddit.read_only = False
        uuid = self.UPDATE_LAYOUT_UUID
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.mod.update_display_layout(None)
        assert collection.display_layout is None

    def test_update_display_layout__timeline(self, reddit):
        reddit.read_only = False
        uuid = self.UPDATE_LAYOUT_UUID
        timeline_layout = "TIMELINE"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.mod.update_display_layout(timeline_layout)
        assert timeline_layout == collection.display_layout

    def test_update_title(self, reddit):
        reddit.read_only = False
        uuid = self.NONEMPTY_REAL_UUID
        new_title = "a" * 100
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections(uuid)
        collection.mod.update_title(new_title)
        assert new_title == collection.title


class TestSubredditCollections(IntegrationTest):
    def test_call(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = next(iter(subreddit.collections))
        assert collection == subreddit.collections(collection.collection_id)
        assert collection == subreddit.collections(permalink=collection.permalink)

    def test_iter(self, reddit):
        found_any = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for collection in subreddit.collections:
            assert collection.permalink
            assert collection.title is not None
            assert collection.description is not None
            found_any = True
        assert found_any


class TestSubredditCollectionsModeration(IntegrationTest):
    def test_create(self, reddit):
        title = "The title!"
        description = "The description."
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections.mod.create(
            title=title, description=description
        )
        assert collection.title == title
        assert collection.description == description
        assert len(collection) == 0

    def test_create__empty_layout(self, reddit):
        title = "The title!"
        description = "The description."
        layout = ""
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections.mod.create(
            title=title, description=description, display_layout=layout
        )
        assert collection.title == title
        assert collection.description == description
        assert collection.display_layout is None
        assert len(collection) == 0

    def test_create__gallery_layout(self, reddit):
        title = "The title!"
        description = "The description."
        layout = "GALLERY"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections.mod.create(
            title=title, description=description, display_layout=layout
        )
        assert collection.title == title
        assert collection.description == description
        assert collection.display_layout == layout
        assert len(collection) == 0

    def test_create__invalid_layout(self, reddit):
        title = "The title!"
        description = "The description."
        layout = "milk before cereal"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException):
            subreddit.collections.mod.create(
                title=title, description=description, display_layout=layout
            )

    def test_create__lowercase_layout(self, reddit):
        title = "The title!"
        description = "The description."
        layout = "gallery"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException):
            subreddit.collections.mod.create(
                title=title, description=description, display_layout=layout
            )

    def test_create__none_layout(self, reddit):
        title = "The title!"
        description = "The description."
        layout = None
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections.mod.create(
            title=title, description=description, display_layout=layout
        )
        assert collection.title == title
        assert collection.description == description
        assert collection.display_layout is None
        assert len(collection) == 0

    def test_create__timeline_layout(self, reddit):
        title = "The title!"
        description = "The description."
        layout = "TIMELINE"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        collection = subreddit.collections.mod.create(
            title=title, description=description, display_layout=layout
        )
        assert collection.title == title
        assert collection.description == description
        assert collection.display_layout == layout
        assert len(collection) == 0
