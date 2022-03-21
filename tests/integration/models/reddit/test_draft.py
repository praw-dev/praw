import pytest

from praw.exceptions import ClientException
from praw.models import Draft, Subreddit

from ... import IntegrationTest


class TestDraft(IntegrationTest):
    def test_create(self):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)

            draft = self.reddit.drafts.create(
                title="test", url="https://reddit.com", subreddit=subreddit
            )
            assert draft.subreddit == subreddit
            assert draft.title == "test"
            assert not hasattr(draft, "selftext")
            assert draft.url == "https://reddit.com"

            draft = self.reddit.drafts.create(
                title="test2", selftext="", subreddit=subreddit
            )
            assert draft.subreddit == subreddit
            assert draft.selftext == ""
            assert draft.title == "test2"
            assert not hasattr(draft, "url")

            draft = self.reddit.drafts.create(
                title="test2",
                selftext="selftext",
                subreddit=pytest.placeholders.test_subreddit,
            )
            assert draft.subreddit == subreddit
            assert draft.selftext == "selftext"
            assert draft.title == "test2"
            assert not hasattr(draft, "url")

    def test_delete(self):
        self.reddit.read_only = False
        with self.use_cassette():
            draft = Draft(self.reddit, id="8f018da6-f0cb-11eb-bac1-aae1fc87c2b4")
            draft.delete()
            assert len(self.reddit.drafts()) == 0

    def test_fetch(self):
        self.reddit.read_only = False
        with self.use_cassette():
            draft = Draft(self.reddit, id="aca27b26-f0d1-11eb-8fde-5e1e94c8225c")
            assert draft.title == "title"
            with pytest.raises(ClientException):
                draft = Draft(self.reddit, id="non-existent")
                draft._fetch()

    def test_list(self):
        self.reddit.read_only = False
        with self.use_cassette():
            assert len(self.reddit.drafts()) == 2

    def test_submit(self):
        self.reddit.read_only = False
        with self.use_cassette():
            total_drafts = len(self.reddit.drafts())

            draft = self.reddit.drafts(draft_id="a5dc88fa-f0da-11eb-8c88-76372e5e5bc0")
            submission = draft.submit()
            assert submission.title == draft.title
            assert submission.selftext == draft.selftext
            assert submission.subreddit != draft.subreddit
            remaining_drafts = len(self.reddit.drafts())
            assert remaining_drafts < total_drafts

    def test_submit__different_subreddit(self):
        self.reddit.read_only = False
        with self.use_cassette():
            total_drafts = len(self.reddit.drafts())

            draft = self.reddit.drafts(draft_id="3d396e12-f0da-11eb-88a1-26b30a152a08")
            submission = draft.submit(
                subreddit=self.reddit.subreddit(pytest.placeholders.test_subreddit)
            )
            assert submission.title == draft.title
            assert submission.subreddit != draft.subreddit
            assert submission.selftext == draft.selftext
            remaining_drafts = len(self.reddit.drafts())
            assert remaining_drafts < total_drafts

            draft = self.reddit.drafts(draft_id="0f4a041c-f0da-11eb-b58a-c230ddc04a99")
            submission = draft.submit(subreddit=pytest.placeholders.test_subreddit)
            assert submission.title == draft.title
            assert submission.selftext == draft.selftext
            assert submission.subreddit != draft.subreddit
            remaining_drafts = len(self.reddit.drafts())
            assert remaining_drafts < total_drafts

    def test_submit__different_title(self):
        self.reddit.read_only = False
        with self.use_cassette():
            total_drafts = len(self.reddit.drafts())

            draft = self.reddit.drafts(draft_id="582b870e-3b72-11ec-b79b-4e8a1c42f3ae")
            new_title = "new title"
            submission = draft.submit(title=new_title)
            assert submission.title == new_title != draft.title
            assert submission.selftext == draft.selftext
            assert str(submission.subreddit) == str(draft.subreddit)
            remaining_drafts = len(self.reddit.drafts())
            assert remaining_drafts < total_drafts

    def test_update(self):
        self.reddit.read_only = False
        with self.use_cassette():
            draft = self.reddit.drafts(draft_id="aca27b26-f0d1-11eb-8fde-5e1e94c8225c")
            assert draft.title == "title"
            draft.update(
                title="new title", subreddit=pytest.placeholders.test_subreddit
            )
            assert draft.title == "new title"
            assert isinstance(draft.subreddit, Subreddit)
            assert draft.subreddit == pytest.placeholders.test_subreddit
