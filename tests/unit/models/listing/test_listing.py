from praw.models.listing.listing import ModmailConversationsListing

from ... import UnitTest


class TestModmailConversationsListing(UnitTest):
    def test_empty_conversations_list(self):
        assert (
            ModmailConversationsListing(self.reddit, _data={"conversations": []}).after
            is None
        )
