"""Test praw.models.LiveThread"""
from unittest import mock

import pytest

from praw.const import API_PATH
from praw.exceptions import RedditAPIException
from praw.models import LiveThread, LiveUpdate, Redditor, RedditorList, Submission

from ... import IntegrationTest


class TestLiveUpdate(IntegrationTest):
    def test_attributes(self):
        update = LiveUpdate(
            self.reddit, "ukaeu1ik4sw5", "7827987a-c998-11e4-a0b9-22000b6a88d2"
        )
        with self.use_cassette():
            assert isinstance(update.author, Redditor)
            assert update.author == "umbrae"
            assert update.name == "LiveUpdate_7827987a-c998-11e4-a0b9-22000b6a88d2"
            assert update.body.startswith("Small change")


class TestLiveThread(IntegrationTest):
    def test_contributor(self):
        thread = LiveThread(self.reddit, "ukaeu1ik4sw5")
        with self.use_cassette():
            contributors = thread.contributor()
        assert isinstance(contributors, RedditorList)
        assert len(contributors) > 0
        for contributor in contributors:
            assert "permissions" in contributor.__dict__
            assert isinstance(contributor, Redditor)

    @mock.patch("time.sleep", return_value=None)
    def test_contributor__with_manage_permission(self, _):
        # see issue #710 for more info
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        url = API_PATH["live_contributors"].format(id=thread.id)
        with self.use_cassette():
            data = thread._reddit.request("GET", url)
            contributors = thread.contributor()
        assert isinstance(data, list)
        assert isinstance(contributors, RedditorList)
        assert len(contributors) > 0

    def test_init(self):
        thread = LiveThread(self.reddit, "ukaeu1ik4sw5")
        with self.use_cassette():
            assert thread.title == "reddit updates"

    def test_discussions(self):
        thread = LiveThread(self.reddit, "ukaeu1ik4sw5")
        with self.use_cassette():
            for submission in thread.discussions(limit=None):
                assert isinstance(submission, Submission)
        assert submission.title == "reddit updates"

    def test_report(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.report("spam")

    @mock.patch("time.sleep", return_value=None)
    def test_updates(self, _):
        thread = LiveThread(self.reddit, "ukaeu1ik4sw5")
        with self.use_cassette():
            for update in thread.updates(limit=None):
                assert update.thread == thread
        assert update.body.startswith("Small change:")


class TestLiveThreadStream(IntegrationTest):
    @property
    def live_thread(self):
        return self.reddit.live("ta535s1hq2je")

    @mock.patch("time.sleep", return_value=None)
    def test_updates(self, _):
        with self.use_cassette():
            generator = self.live_thread.stream.updates()
            for i in range(101):
                assert isinstance(next(generator), LiveUpdate)


class TestLiveContributorRelationship(IntegrationTest):
    def test_accept_invite(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.accept_invite()

    @mock.patch("time.sleep", return_value=None)
    def test_invite__already_invited(self, _):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.invite("nmtake")
            with pytest.raises(RedditAPIException) as excinfo:
                thread.contributor.invite("nmtake")
        assert excinfo.value.items[0].error_type == "LIVEUPDATE_ALREADY_CONTRIBUTOR"

    def test_invite__empty_list(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.invite("nmtake", [])

    def test_invite__limited(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.invite("nmtake", ["manage", "edit"])

    def test_invite__none(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.invite("nmtake", None)

    def test_invite__redditor(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        redditor = Redditor(self.reddit, _data={"name": "nmtake", "id": "ll32z"})
        with self.use_cassette():
            thread.contributor.invite(redditor)

    def test_leave(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.leave()

    def test_remove__fullname(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.remove("t2_ll32z")

    def test_remove__redditor(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        redditor = Redditor(self.reddit, _data={"name": "nmtake", "id": "ll32z"})
        with self.use_cassette():
            thread.contributor.remove(redditor)

    def test_remove_invite__fullname(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contributor.remove_invite("t2_ll32z")

    def test_remove_invite__redditor(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        redditor = Redditor(self.reddit, _data={"name": "nmtake", "id": "ll32z"})
        with self.use_cassette():
            thread.contributor.remove_invite(redditor)

    def test_update__empty_list(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.contributor.update("nmtake", [])

    def test_update__limited(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.contributor.update("nmtake", ["manage", "edit"])

    def test_update__none(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.contributor.update("nmtake", None)

    def test_update_invite__empty_list(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.contributor.update_invite("nmtake", [])

    def test_update_invite__limited(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.contributor.update_invite("nmtake", ["manage", "edit"])

    def test_update_invite__none(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ydwwxneu7vsa")
        with self.use_cassette():
            thread.contributor.update_invite("nmtake", None)


class TestLiveThreadContribution(IntegrationTest):
    def test_add(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contrib.add("* `LiveThreadContribution.add() test`")

    def test_close(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "ya2tmqiyb064")
        with self.use_cassette():
            thread.contrib.close()

    @mock.patch("time.sleep", return_value=None)
    def test_update__partial_settings(self, _):
        old_settings = {
            "title": "old title",
            "description": "## old description",
            "nsfw": False,
            "resources": "## old resources",
        }
        new_settings = {"title": "new title", "nsfw": True}
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contrib.update(**new_settings)
            assert thread.title == new_settings["title"]
            assert thread.description == old_settings["description"]
            assert thread.nsfw == new_settings["nsfw"]
            assert thread.resources == old_settings["resources"]

    @mock.patch("time.sleep", return_value=None)
    def test_update__full_settings(self, _):
        new_settings = {
            "title": "new title 2",
            "description": "## new description 2",
            "nsfw": True,
            "resources": "## new resources 2",
        }
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contrib.update(**new_settings)
            assert thread.title == new_settings["title"]
            assert thread.description == new_settings["description"]
            assert thread.nsfw == new_settings["nsfw"]
            assert thread.resources == new_settings["resources"]

    @mock.patch("time.sleep", return_value=None)
    def test_update__other_settings(self, _):
        new_settings = {
            "title": "new title",
            "other1": "other 1",
            "other2": "other 2",
        }
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        with self.use_cassette():
            thread.contrib.update(**new_settings)


class TestLiveUpdateContribution(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        update = LiveUpdate(
            self.reddit, "xyu8kmjvfrww", "5d556760-dbee-11e6-9f46-0e78de675452"
        )
        with self.use_cassette():
            update.contrib.remove()

    def test_strike(self):
        self.reddit.read_only = False
        update = LiveUpdate(
            self.reddit, "xyu8kmjvfrww", "cb5fe532-dbee-11e6-9a91-0e6d74fabcc4"
        )
        with self.use_cassette():
            update.contrib.strike()
