from base64 import urlsafe_b64encode

import pytest
from prawcore import Forbidden, NotFound

from praw.exceptions import RedditAPIException
from praw.models import Redditor, WikiPage

from ... import IntegrationTest


def large_content():
    with open("tests/integration/files/too_large.jpg", "rb") as fp:
        return urlsafe_b64encode(fp.read()).decode()


class TestWikiPageModeration(IntegrationTest):
    def test_add(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        page.mod.add("bboe")

    def test_remove(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        page.mod.remove("bboe")

    def test_revert(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        revision_id = next(page.revisions(limit=1))["id"]
        page.revision(revision_id).mod.revert()

    def test_revert_css_fail(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "config/stylesheet")

        reddit.read_only = False
        subreddit.stylesheet.upload(
            name="css-revert-fail",
            image_path="tests/integration/files/icon.jpg",
        )
        page.edit(content="div {background: url(%%css-revert-fail%%)}")
        revision_id = next(page.revisions(limit=1))["id"]
        subreddit.stylesheet.delete_image("css-revert-fail")
        with pytest.raises(Forbidden) as exc:
            page.revision(revision_id).mod.revert()
        assert exc.value.response.json() == {
            "reason": "INVALID_CSS",
            "message": "Forbidden",
            "explanation": "%(css_error)s",
        }

    def test_settings(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        settings = page.mod.settings()
        assert {"editors": [], "listed": True, "permlevel": 0} == settings

    def test_update(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        updated = page.mod.update(listed=False, permlevel=1)
        assert {"editors": [], "listed": False, "permlevel": 1} == updated


class TestWikiPage(IntegrationTest):
    def test_content_md(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")
        assert page.content_md

    def test_content_md__invalid_name(self, reddit):
        subreddit = reddit.subreddit("reddit.com")
        page = WikiPage(reddit, subreddit, "\\A")
        with pytest.raises(RedditAPIException) as excinfo:
            page.content_md
        assert str(excinfo.value) == "INVALID_PAGE_NAME"

    def test_discussions(self, reddit):
        subreddit = reddit.subreddit("reddit.com")
        page = WikiPage(reddit, subreddit, "search")
        assert list(page.discussions())

    def test_edit(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        page.edit(content="PRAW updated")

    @pytest.mark.add_placeholder(content=large_content())
    def test_edit__usernotes(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "usernotes")
        reddit.read_only = False
        page.edit(content=large_content())

    def test_edit__with_reason(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")

        reddit.read_only = False
        page.edit(content="PRAW updated with reason", reason="PRAW testing")

    def test_init__with_revision(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(
            reddit,
            subreddit,
            "index",
            revision="2f38e910-b109-11e2-ba44-12313b0d4e76",
        )
        assert isinstance(page.revision_by, Redditor)
        assert page.revision_date == 1367295177

    def test_init__with_revision__author_deleted(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(
            reddit,
            subreddit,
            "index",
            revision="873933a0-5550-11e2-82f1-12313b0c1e2b",
        )
        assert page.revision_by is None

    def test_invalid_page(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "invalid")
        with pytest.raises(NotFound):
            page.content_md

    def test_revision(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        revision_id = "f31e1988-07d0-11e6-b927-0ea0743a0543"
        page = subreddit.wiki["index"].revision(revision_id)
        assert len(page.content_md) > 0

    def test_revision_by(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        page = WikiPage(reddit, subreddit, "test")
        assert isinstance(page.revision_by, Redditor)

    def test_revisions(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        count = 0
        for revision in subreddit.wiki["index"].revisions(limit=None):
            count += 1
            assert isinstance(revision["author"], Redditor)
            assert isinstance(revision["page"], WikiPage)
        assert count > 0

    def test_revisions__author_deleted(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        revisions = subreddit.wiki["index"].revisions(limit=10)
        assert any(revision["author"] is None for revision in revisions)
