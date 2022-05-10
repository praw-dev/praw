from praw.models.listing.listing import ModmailConversationsListing, ModNoteListing

from ... import UnitTest


class TestModmailConversationsListing(UnitTest):
    def test_empty_conversations_list(self):
        assert (
            ModmailConversationsListing(self.reddit, _data={"conversations": []}).after
            is None
        )


class TestModNoteListing(UnitTest):
    def test_has_next_page(self):
        assert (
            ModNoteListing(
                self.reddit, _data={"has_next_page": True, "end_cursor": "end_cursor"}
            ).after
            == "end_cursor"
        )
