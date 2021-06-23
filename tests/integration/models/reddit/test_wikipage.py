from base64 import urlsafe_b64encode
from unittest import mock

import pytest
from prawcore import Forbidden, NotFound

from praw.exceptions import RedditAPIException
from praw.models import Redditor, WikiPage

from ... import IntegrationTest


class TestWikiPage(IntegrationTest):
    def test_content_md(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        with self.use_cassette():
            assert page.content_md

    def test_content_md__invalid_name(self):
        subreddit = self.reddit.subreddit("reddit.com")
        page = WikiPage(self.reddit, subreddit, "\\A")

        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                page.content_md
            assert str(excinfo.value) == "INVALID_PAGE_NAME"

    def test_discussions(self):
        subreddit = self.reddit.subreddit("reddit.com")
        page = WikiPage(self.reddit, subreddit, "search")

        with self.use_cassette():
            assert list(page.discussions())

    def test_edit(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            page.edit("PRAW updated")

    def test_edit__usernotes(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "usernotes")
        with open("tests/integration/files/too_large.jpg", "rb") as fp:
            large_content = urlsafe_b64encode(fp.read()).decode()

        self.reddit.read_only = False
        with self.use_cassette(
            placeholders=self.recorder.configure().default_cassette_options[
                "placeholders"
            ]
            + [{"placeholder": "<CONTENT>", "replace": large_content}]
        ):
            page.edit(large_content)

    def test_edit__with_reason(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            page.edit("PRAW updated with reason", reason="PRAW testing")

    def test_init__with_revision(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(
            self.reddit,
            subreddit,
            "index",
            revision="2f38e910-b109-11e2-ba44-12313b0d4e76",
        )
        with self.use_cassette():
            assert isinstance(page.revision_by, Redditor)
            assert page.revision_date == 1367295177

    def test_init__with_revision__author_deleted(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(
            self.reddit,
            subreddit,
            "index",
            revision="873933a0-5550-11e2-82f1-12313b0c1e2b",
        )
        with self.use_cassette():
            assert page.revision_by is None

    def test_invalid_page(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "invalid")
        with self.use_cassette():
            with pytest.raises(NotFound):
                page.content_md

    def test_revision_by(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        with self.use_cassette():
            assert isinstance(page.revision_by, Redditor)

    def test_revision(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        revision_id = "f31e1988-07d0-11e6-b927-0ea0743a0543"
        page = subreddit.wiki["index"].revision(revision_id)

        with self.use_cassette():
            assert len(page.content_md) > 0

    @mock.patch("time.sleep", return_value=None)
    def test_revisions(self, _):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)

        with self.use_cassette():
            count = 0
            for revision in subreddit.wiki["index"].revisions(limit=None):
                count += 1
                assert isinstance(revision["author"], Redditor)
                assert isinstance(revision["page"], WikiPage)
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_revisions__author_deleted(self, _):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)

        with self.use_cassette():
            revisions = subreddit.wiki["index"].revisions(limit=10)
            assert any(revision["author"] is None for revision in revisions)


class TestWikiPageModeration(IntegrationTest):
    def test_add(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            page.mod.add("bboe")

    def test_remove(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            page.mod.remove("bboe")

    @mock.patch("time.sleep", return_value=None)
    def test_revert(self, _):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            revision_id = next(page.revisions(limit=1))["id"]
            page.revision(revision_id).mod.revert()

    @mock.patch("time.sleep", return_value=None)
    def test_revert_css_fail(self, _):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "config/stylesheet")

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit.stylesheet.upload(
                name="css-revert-fail",
                image_path="tests/integration/files/icon.jpg",
            )
            page.edit("div {background: url(%%css-revert-fail%%)}")
            revision_id = next(page.revisions(limit=1))["id"]
            subreddit.stylesheet.delete_image("css-revert-fail")
            with pytest.raises(Forbidden) as exc:
                page.revision(revision_id).mod.revert()
            assert exc.value.response.json() == {
                "reason": "INVALID_CSS",
                "message": "Forbidden",
                "explanation": "%(css_error)s",
            }

    def test_settings(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            settings = page.mod.settings()
        assert {"editors": [], "listed": True, "permlevel": 0} == settings

    def test_update(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(self.reddit, subreddit, "test")

        self.reddit.read_only = False
        with self.use_cassette():
            updated = page.mod.update(listed=False, permlevel=1)
        assert {"editors": [], "listed": False, "permlevel": 1} == updated
