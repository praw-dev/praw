"""Test praw.models.reddit.announcement."""

from praw.models import Announcement
from praw.models.listing.generator import ListingGenerator

from ... import IntegrationTest


class TestAnnouncement(IntegrationTest):
    def test_hide(self, reddit):
        reddit.read_only = False
        announcement = next(reddit.announcements())
        announcement.hide()

    def test_mark_read(self, reddit):
        reddit.read_only = False
        announcement = next(reddit.announcements())
        announcement.mark_read()
        # Re-fetch the same announcement to confirm read_at is now set.
        refreshed = next(a for a in reddit.announcements() if a.id == announcement.id)
        assert refreshed.read_at is not None


class TestAnnouncementHelper(IntegrationTest):
    def test_call(self, reddit):
        reddit.read_only = False
        generator = reddit.announcements()
        assert isinstance(generator, ListingGenerator)
        count = 0
        for announcement in generator:
            assert isinstance(announcement, Announcement)
            assert announcement.id.startswith("ann_")
            assert announcement.fullname == announcement.id
            count += 1
        assert count > 0

    def test_call__with_limit(self, reddit):
        reddit.read_only = False
        announcements = list(reddit.announcements(limit=5))
        assert len(announcements) == 5
        assert all(isinstance(a, Announcement) for a in announcements)

    def test_call__pagination(self, reddit):
        reddit.read_only = False
        # Drive pagination by requesting more than fits in a single response.
        announcements = list(reddit.announcements(limit=4, request_limit=2))
        assert len(announcements) > 2
        # Ensure no duplicates across pages.
        ids = [a.id for a in announcements]
        assert len(set(ids)) == len(ids)

    def test_hide(self, reddit):
        reddit.read_only = False
        announcements = list(reddit.announcements(limit=2))
        reddit.announcements.hide(announcements)

    def test_mark_all_read(self, reddit):
        reddit.read_only = False
        reddit.announcements.mark_all_read()
        for announcement in reddit.announcements(limit=10):
            assert announcement.read_at is not None

    def test_mark_read(self, reddit):
        reddit.read_only = False
        unread = [a for a in reddit.announcements(limit=25) if a.read_at is None]
        reddit.announcements.mark_read(unread)
        unread_ids = {a.id for a in unread}
        for announcement in reddit.announcements(limit=25):
            if announcement.id in unread_ids:
                assert announcement.read_at is not None
