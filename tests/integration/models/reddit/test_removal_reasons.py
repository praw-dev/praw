import pytest

from praw.exceptions import ClientException
from praw.models import RemovalReason

from ... import IntegrationTest


class TestRemovalReason(IntegrationTest):
    def test__fetch(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons["110nhral8vygf"]
        assert reason.title.startswith("Be Kind")

    def test__fetch__invalid_reason(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons["invalid"]
        with pytest.raises(ClientException) as excinfo:
            reason.title
        assert str(excinfo.value) == (
            f"Subreddit {subreddit} does not have the removal reason invalid"
        )

    @pytest.mark.cassette_name("TestRemovalReason.test__fetch")
    def test__fetch_int(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons[0]
        assert isinstance(reason, RemovalReason)

    @pytest.mark.cassette_name("TestRemovalReason.test__fetch")
    def test__fetch_slice(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reasons = subreddit.mod.removal_reasons[-3:]
        assert len(reasons) == 3
        for reason in reasons:
            assert isinstance(reason, RemovalReason)

    def test_delete(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons["110nhyk34m01d"]
        reason.delete()

    def test_update(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons["110nhk2cgmaxy"]
        reason.update(title="New Title", message="New Message")

    def test_update_empty(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons[1]
        reason.update()


class TestSubredditRemovalReasons(IntegrationTest):
    def test__iter(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for reason in subreddit.mod.removal_reasons:
            assert isinstance(reason, RemovalReason)
            count += 1
        assert count > 0

    def test_add(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.mod.removal_reasons.add(title="Test", message="test")
        assert isinstance(reason, RemovalReason)
