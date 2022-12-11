from praw.models.listing.listing import ModmailConversationsListing, ModNoteListing

from ... import UnitTest


class TestModNoteListing(UnitTest):
    def test_has_next_page(self, reddit):
        assert (
            ModNoteListing(
                reddit, _data={"has_next_page": True, "end_cursor": "end_cursor"}
            ).after
            == "end_cursor"
        )


class TestModmailConversationsListing(UnitTest):
    def test_empty_conversations_list(self, reddit):
        assert (
            ModmailConversationsListing(reddit, _data={"conversations": []}).after
            is None
        )
