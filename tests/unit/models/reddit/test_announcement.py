import pickle
from unittest import mock

import pytest

from praw.const import API_PATH
from praw.models import Announcement, AnnouncementListing
from praw.models.listing.generator import ListingGenerator

from ... import UnitTest


class TestAnnouncement(UnitTest):
    def test_construct_failure(self, reddit):
        message = "Exactly one of 'id' or '_data' must be provided."
        with pytest.raises(TypeError) as excinfo:
            Announcement(reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Announcement(reddit, "ann_x", _data={"id": "ann_x"})
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Announcement(reddit, id="ann_x", _data={"id": "ann_x"})
        assert str(excinfo.value) == message

    def test_equality(self, reddit):
        a1 = Announcement(reddit, _data={"id": "ann_a"})
        a2 = Announcement(reddit, _data={"id": "ann_a"})
        a3 = Announcement(reddit, _data={"id": "ann_b"})
        assert a1 == a2
        assert a1 != a3
        assert a1 == "ann_a"

    def test_fullname(self, reddit):
        announcement = Announcement(reddit, _data={"id": "ann_4sc833"})
        assert announcement.fullname == "ann_4sc833"

    def test_fullname_via_id(self, reddit):
        announcement = Announcement(reddit, id="ann_4sc833")
        assert announcement.fullname == "ann_4sc833"

    def test_hash(self, reddit):
        a1 = Announcement(reddit, _data={"id": "ann_a"})
        a2 = Announcement(reddit, _data={"id": "ann_a"})
        a3 = Announcement(reddit, _data={"id": "ann_b"})
        assert hash(a1) == hash(a2)
        assert hash(a1) != hash(a3)

    def test_kind(self, reddit):
        assert Announcement(reddit, id="ann_x")._kind == "ann"

    def test_pickle(self, reddit):
        announcement = Announcement(reddit, _data={"id": "ann_x"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(announcement, protocol=level))
            assert announcement == other

    def test_repr(self, reddit):
        announcement = Announcement(reddit, id="ann_4sc833")
        assert repr(announcement) == "Announcement(id='ann_4sc833')"

    def test_str(self, reddit):
        announcement = Announcement(reddit, _data={"id": "ann_4sc833"})
        assert str(announcement) == "ann_4sc833"

    def test_hide(self, reddit):
        announcement = Announcement(reddit, id="ann_4sc833")
        with mock.patch.object(reddit, "post") as post:
            announcement.hide()
        post.assert_called_once_with(API_PATH["hide_announcements"], data={"ids": "ann_4sc833"})

    def test_mark_read(self, reddit):
        announcement = Announcement(reddit, id="ann_4sc833")
        with mock.patch.object(reddit, "post") as post:
            announcement.mark_read()
        post.assert_called_once_with(API_PATH["read_announcements"], data={"ids": "ann_4sc833"})

    def test_objector_builds_listing(self, reddit):
        payload = {
            "after": "ann_next",
            "before": "",
            "data": [
                {
                    "id": "ann_d50580",
                    "subject": "Mod Monthly",
                    "body": "b",
                    "body_html": "<p>b</p>",
                    "permalink": "https://www.reddit.com/notifications/a/ann_d50580",
                    "read_at": None,
                    "sent_at": "2026-06-08T18:07:46Z",
                },
                {
                    "id": "ann_cqzpay",
                    "subject": "Thanks",
                    "body": "b",
                    "body_html": "<p>b</p>",
                    "permalink": "https://www.reddit.com/notifications/a/ann_cqzpay",
                    "read_at": "2026-06-03T14:12:57Z",
                    "sent_at": "2026-05-29T21:07:52Z",
                },
            ],
        }
        result = reddit._objector.objectify(data=payload)
        assert isinstance(result, AnnouncementListing)
        assert result.after == "ann_next"
        assert len(result) == 2
        assert all(isinstance(child, Announcement) for child in result)
        assert result[0].id == "ann_d50580"
        assert result[1].read_at == "2026-06-03T14:12:57Z"

    def test_data_populates_attributes(self, reddit):
        data = {
            "id": "ann_d50580",
            "subject": "Mod Monthly",
            "body": "body",
            "body_html": "<p>body</p>",
            "permalink": "https://www.reddit.com/notifications/a/ann_d50580",
            "read_at": None,
            "sent_at": "2026-06-08T18:07:46Z",
        }
        announcement = Announcement(reddit, _data=data)
        assert announcement.id == "ann_d50580"
        assert announcement.subject == "Mod Monthly"
        assert announcement.read_at is None
        assert announcement._fetched is True


class TestAnnouncementHelper(UnitTest):
    def _ann(self, reddit, ident):
        return Announcement(reddit, id=ident)

    def test_call_returns_listing_generator(self, reddit):
        gen = reddit.announcements()
        assert isinstance(gen, ListingGenerator)
        assert gen.url == API_PATH["announcements"]

    def test_call_passes_generator_kwargs(self, reddit):
        gen = reddit.announcements(limit=5)
        assert gen.limit == 5

    def test_mark_all_read(self, reddit):
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.mark_all_read()
        post.assert_called_once_with(API_PATH["read_all_announcements"])

    def test_mark_read(self, reddit):
        announcements = [self._ann(reddit, f"ann_{i}") for i in range(3)]
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.mark_read(announcements)
        post.assert_called_once_with(API_PATH["read_announcements"], data={"ids": "ann_0,ann_1,ann_2"})

    def test_mark_read_batches_at_100(self, reddit):
        announcements = [self._ann(reddit, f"ann_{i}") for i in range(150)]
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.mark_read(announcements)
        assert post.call_count == 2
        first_ids = post.call_args_list[0].kwargs["data"]["ids"].split(",")
        second_ids = post.call_args_list[1].kwargs["data"]["ids"].split(",")
        assert len(first_ids) == 100
        assert len(second_ids) == 50

    def test_mark_read_empty(self, reddit):
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.mark_read([])
        post.assert_not_called()

    def test_hide(self, reddit):
        announcements = [self._ann(reddit, f"ann_{i}") for i in range(2)]
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.hide(announcements)
        post.assert_called_once_with(API_PATH["hide_announcements"], data={"ids": "ann_0,ann_1"})

    def test_hide_batches_at_100(self, reddit):
        announcements = [self._ann(reddit, f"ann_{i}") for i in range(201)]
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.hide(announcements)
        assert post.call_count == 3

    def test_hide_empty(self, reddit):
        with mock.patch.object(reddit, "post") as post:
            reddit.announcements.hide([])
        post.assert_not_called()
