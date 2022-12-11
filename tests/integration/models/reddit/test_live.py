"""Test praw.models.LiveThread"""

import pytest

from praw.const import API_PATH
from praw.exceptions import RedditAPIException
from praw.models import LiveThread, LiveUpdate, Redditor, RedditorList, Submission

from ... import IntegrationTest


class TestLiveContributorRelationship(IntegrationTest):
    def test_accept_invite(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.accept_invite()

    def test_invite__already_invited(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.invite("nmtake")
        with pytest.raises(RedditAPIException) as excinfo:
            thread.contributor.invite("nmtake")
        assert excinfo.value.items[0].error_type == "LIVEUPDATE_ALREADY_CONTRIBUTOR"

    def test_invite__empty_list(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.invite("nmtake", permissions=[])

    def test_invite__limited(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.invite("nmtake", permissions=["manage", "edit"])

    def test_invite__none(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.invite("nmtake", permissions=None)

    def test_invite__redditor(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        redditor = Redditor(reddit, _data={"name": "nmtake", "id": "ll32z"})
        thread.contributor.invite(redditor)

    def test_leave(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.leave()

    def test_remove__fullname(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.remove("t2_ll32z")

    def test_remove__redditor(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        redditor = Redditor(reddit, _data={"name": "nmtake", "id": "ll32z"})
        thread.contributor.remove(redditor)

    def test_remove_invite__fullname(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contributor.remove_invite("t2_ll32z")

    def test_remove_invite__redditor(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        redditor = Redditor(reddit, _data={"name": "nmtake", "id": "ll32z"})
        thread.contributor.remove_invite(redditor)

    def test_update__empty_list(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.contributor.update("nmtake", permissions=[])

    def test_update__limited(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.contributor.update("nmtake", permissions=["manage", "edit"])

    def test_update__none(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.contributor.update("nmtake", permissions=None)

    def test_update_invite__empty_list(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.contributor.update_invite("nmtake", permissions=[])

    def test_update_invite__limited(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.contributor.update_invite("nmtake", permissions=["manage", "edit"])

    def test_update_invite__none(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.contributor.update_invite("nmtake", permissions=None)


class TestLiveThread(IntegrationTest):
    def test_contributor(self, reddit):
        thread = LiveThread(reddit, "ukaeu1ik4sw5")
        contributors = thread.contributor()
        assert isinstance(contributors, RedditorList)
        assert len(contributors) > 0
        for contributor in contributors:
            assert "permissions" in contributor.__dict__
            assert isinstance(contributor, Redditor)

    def test_contributor__with_manage_permission(self, reddit):
        # see issue #710 for more info
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        url = API_PATH["live_contributors"].format(id=thread.id)
        data = thread._reddit.request(method="GET", path=url)
        contributors = thread.contributor()
        assert isinstance(data, list)
        assert isinstance(contributors, RedditorList)
        assert len(contributors) > 0

    def test_discussions(self, reddit):
        thread = LiveThread(reddit, "ukaeu1ik4sw5")
        for submission in thread.discussions(limit=None):
            assert isinstance(submission, Submission)
        assert submission.title == "reddit updates"

    def test_init(self, reddit):
        thread = LiveThread(reddit, "ukaeu1ik4sw5")
        assert thread.title == "reddit updates"

    def test_report(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ydwwxneu7vsa")
        thread.report("spam")

    def test_updates(self, reddit):
        thread = LiveThread(reddit, "ukaeu1ik4sw5")
        for update in thread.updates(limit=None):
            assert update.thread == thread
        assert update.body.startswith("Small change:")


class TestLiveThreadContribution(IntegrationTest):
    def test_add(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contrib.add("* `LiveThreadContribution.add() test`")

    def test_close(self, reddit):
        reddit.read_only = False
        thread = LiveThread(reddit, "ya2tmqiyb064")
        thread.contrib.close()

    def test_update__full_settings(self, reddit):
        new_settings = {
            "title": "new title 2",
            "description": "## new description 2",
            "nsfw": True,
            "resources": "## new resources 2",
        }
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contrib.update(**new_settings)
        assert thread.title == new_settings["title"]
        assert thread.description == new_settings["description"]
        assert thread.nsfw == new_settings["nsfw"]
        assert thread.resources == new_settings["resources"]

    def test_update__other_settings(self, reddit):
        new_settings = {
            "title": "new title",
            "other1": "other 1",
            "other2": "other 2",
        }
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contrib.update(**new_settings)

    def test_update__partial_settings(self, reddit):
        old_settings = {
            "title": "old title",
            "description": "## old description",
            "nsfw": False,
            "resources": "## old resources",
        }
        new_settings = {"title": "new title", "nsfw": True}
        reddit.read_only = False
        thread = LiveThread(reddit, "xyu8kmjvfrww")
        thread.contrib.update(**new_settings)
        assert thread.title == new_settings["title"]
        assert thread.description == old_settings["description"]
        assert thread.nsfw == new_settings["nsfw"]
        assert thread.resources == old_settings["resources"]


class TestLiveThreadStream(IntegrationTest):
    def test_updates(self, reddit):
        live_thread = reddit.live("ta535s1hq2je")
        generator = live_thread.stream.updates()
        for i in range(101):
            assert isinstance(next(generator), LiveUpdate)


class TestLiveUpdate(IntegrationTest):
    def test_attributes(self, reddit):
        update = LiveUpdate(
            reddit, "ukaeu1ik4sw5", "7827987a-c998-11e4-a0b9-22000b6a88d2"
        )
        assert isinstance(update.author, Redditor)
        assert update.author == "umbrae"
        assert update.name == "LiveUpdate_7827987a-c998-11e4-a0b9-22000b6a88d2"
        assert update.body.startswith("Small change")


class TestLiveUpdateContribution(IntegrationTest):
    def test_remove(self, reddit):
        reddit.read_only = False
        update = LiveUpdate(
            reddit, "xyu8kmjvfrww", "5d556760-dbee-11e6-9f46-0e78de675452"
        )
        update.contrib.remove()

    def test_strike(self, reddit):
        reddit.read_only = False
        update = LiveUpdate(
            reddit, "xyu8kmjvfrww", "cb5fe532-dbee-11e6-9a91-0e6d74fabcc4"
        )
        update.contrib.strike()
