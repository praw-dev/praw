from unittest import mock

import pytest

from praw.exceptions import ClientException, PRAWException, RedditAPIException
from praw.models import Comment, Submission

from ... import IntegrationTest


class TestComment(IntegrationTest):
    def test_attributes(self):
        with self.use_cassette():
            comment = Comment(self.reddit, "cklhv0f")
            assert comment.author == "bboe"
            assert comment.body.startswith("Yes it does.")
            assert not comment.is_root
            assert comment.submission == "2gmzqe"

    @mock.patch("time.sleep", return_value=None)
    def test_block(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = None
            for item in self.reddit.inbox.submission_replies():
                if item.author and item.author != pytest.placeholders.username:
                    comment = item
                    break
            else:
                assert False, "no comment found"
            comment.block()

    def test_clear_vote(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "d1680wu").clear_vote()

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = Comment(self.reddit, "d1616q2")
            comment.delete()
            assert comment.author is None
            assert comment.body == "[deleted]"

    def test_disable_inbox_replies(self):
        self.reddit.read_only = False
        comment = Comment(self.reddit, "dcc9snh")
        with self.use_cassette():
            comment.disable_inbox_replies()

    def test_downvote(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "d1680wu").downvote()

    @mock.patch("time.sleep", return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = Comment(self.reddit, "d1616q2")
            comment.edit("New text")
            assert comment.body == "New text"

    def test_enable_inbox_replies(self):
        self.reddit.read_only = False
        comment = Comment(self.reddit, "dcc9snh")
        with self.use_cassette():
            comment.enable_inbox_replies()

    def test_award(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_award"):
            award_data = Comment(self.reddit, "g7cmlgc").award()
            assert award_data["gildings"]["gid_2"] == 1

    def test_award__not_enough_coins(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                Comment(self.reddit, "g7cmlgc").award(
                    gild_type="award_2385c499-a1fb-44ec-b9b7-d260f3dc55de"
                )
            exception = excinfo.value
            assert "INSUFFICIENT_COINS_WITH_AMOUNT" == exception.error_type

    def test_award__self_gild(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_award__self_gild"):
            with pytest.raises(RedditAPIException) as excinfo:
                Comment(self.reddit, "g7cn9xb").award(
                    gild_type="award_2385c499-a1fb-44ec-b9b7-d260f3dc55de"
                )
            exception = excinfo.value
            assert "SELF_GILDING_NOT_ALLOWED" == exception.error_type

    def test_gild(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_award"):
            award_data = Comment(self.reddit, "g7cmlgc").gild()
            assert award_data["gildings"]["gid_2"] == 1

    def test_invalid(self):
        with self.use_cassette():
            with pytest.raises(PRAWException) as excinfo:
                Comment(self.reddit, "0").body
            assert excinfo.value.args[0].startswith("No data returned for comment")

    @mock.patch("time.sleep", return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = next(self.reddit.inbox.unread())
            assert isinstance(comment, Comment)
            comment.mark_read()

    @mock.patch("time.sleep", return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = next(self.reddit.inbox.comment_replies())
            comment.mark_unread()

    def test_parent__comment(self):
        comment = Comment(self.reddit, "cklhv0f")
        with self.use_cassette():
            parent = comment.parent()
            parent.refresh()
            assert comment in parent.replies
        assert isinstance(parent, Comment)
        assert parent.fullname == comment.parent_id

    def test_parent__chain(self):
        comment = Comment(self.reddit, "dkk4qjd")
        counter = 0
        with self.use_cassette():
            comment.refresh()
            parent = comment.parent()
            while parent != comment.submission:
                if counter % 9 == 0:
                    parent.refresh()
                counter += 1
                parent = parent.parent()

    def test_parent__comment_from_forest(self):
        submission = self.reddit.submission("2gmzqe")
        with self.use_cassette():
            comment = submission.comments[0].replies[0]
        parent = comment.parent()
        assert comment in parent.replies
        assert isinstance(parent, Comment)
        assert parent.fullname == comment.parent_id

    @mock.patch("time.sleep", return_value=None)
    def test_parent__from_replies(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = next(self.reddit.inbox.comment_replies())
        parent = comment.parent()
        assert isinstance(parent, Comment)
        assert parent.fullname == comment.parent_id

    def test_parent__submission(self):
        comment = Comment(self.reddit, "cklfmye")
        with self.use_cassette():
            parent = comment.parent()
            assert comment in parent.comments
        assert isinstance(parent, Submission)
        assert parent.fullname == comment.parent_id

    def test_refresh(self):
        comment = Comment(self.reddit, "d81vwef")
        with self.use_cassette():
            assert len(comment.replies) == 0
            comment.refresh()
            assert len(comment.replies) > 0

    def test_refresh__raises_exception(self):
        with self.use_cassette():
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, "d81vwef").refresh()
        assert (
            "This comment does not appear to be in the comment tree",
        ) == excinfo.value.args

    def test_refresh__twice(self):
        with self.use_cassette():
            Comment(self.reddit, "d81vwef").refresh().refresh()

    def test_refresh__deleted_comment(self):
        with self.use_cassette():
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, "d7ltvl0").refresh()
        assert (
            "This comment does not appear to be in the comment tree",
        ) == excinfo.value.args

    def test_refresh__removed_comment(self):
        with self.use_cassette():
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, "dma3mi5").refresh()
        assert (
            "This comment does not appear to be in the comment tree",
        ) == excinfo.value.args

    def test_refresh__with_reply_sort_and_limit(self):
        with self.use_cassette():
            comment = Comment(self.reddit, "e4j4830")
            comment.reply_limit = 4
            comment.reply_sort = "new"
            comment.refresh()
            replies = comment.replies
        last_created = float("inf")
        for reply in replies:
            if isinstance(reply, Comment):
                if reply.created_utc > last_created:
                    assert False, "sort order incorrect"
                last_created = reply.created_utc
        assert len(comment.replies) == 3

    def test_reply(self):
        self.reddit.read_only = False
        with self.use_cassette():
            parent_comment = Comment(self.reddit, "d1616q2")
            comment = parent_comment.reply("Comment reply")
            assert comment.author == self.reddit.config.username
            assert comment.body == "Comment reply"
            assert not comment.is_root
            assert comment.parent_id == parent_comment.fullname

    def test_reply__none(self):
        self.reddit.read_only = False
        comment = Comment(self.reddit, "eear2ml")
        with self.use_cassette():
            reply = comment.reply("TEST")
        assert reply is None

    def test_report(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "d0335z3").report("custom")

    def test_save(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "d1680wu").save("foo")

    def test_unsave(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "d1680wu").unsave()

    def test_upvote(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "d1680wu").upvote()


class TestCommentModeration(IntegrationTest):
    def test_approve(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "da2g5y6").mod.approve()

    def test_distinguish(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "da2g5y6").mod.distinguish()

    @mock.patch("time.sleep", return_value=None)
    def test_distinguish__sticky(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "da2g5y6").mod.distinguish(sticky=True)

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.comment("da2g5y6").mod.ignore_reports()

    def test_lock(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "da2g6ne").mod.lock()

    def test_remove(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.comment("da2g5y6").mod.remove(spam=True)

    @mock.patch("time.sleep", return_value=None)
    def test_remove_with_reason_id(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.comment("f3dm3b7").mod.remove(reason_id="110nhral8vygf")

    def test_show(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.comment("fjyyrv6").mod.show()

    def test_unlock(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Comment(self.reddit, "da2g6ne").mod.unlock()

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = self.reddit.comment("f98ukt5")
            comment.mod.remove()
            comment.mod._add_removal_reason(mod_note="Blah", reason_id="110nhral8vygf")

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason_without_id(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = self.reddit.comment("f98ugot")
            comment.mod.remove()
            comment.mod._add_removal_reason(mod_note="Test")

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason_without_id_or_note(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(ValueError) as excinfo:
                comment = self.reddit.comment("f9974ce")
                comment.mod.remove()
                comment.mod._add_removal_reason()
            assert excinfo.value.args[0].startswith("mod_note cannot be blank")

    @mock.patch("time.sleep", return_value=None)
    def test_send_removal_message(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = self.reddit.comment("edu698v")
            mod = comment.mod
            mod.remove()
            message = "message"
            res = [
                mod.send_removal_message(message, "title", type)
                for type in ("public", "private", "private_exposed")
            ]
            assert isinstance(res[0], Comment)
            assert res[0].parent_id == f"t1_{comment.id}"
            assert res[0].body == message
            assert res[1] is None
            assert res[2] is None

    @mock.patch("time.sleep", return_value=None)
    def test_send_removal_message__error(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            comment = self.reddit.comment("fkmrn4a")
            comment.mod.remove()
            with pytest.raises(RedditAPIException) as excinfo:
                comment.mod.send_removal_message("message", "a" * 51)
            exception = excinfo.value
            assert "title" == exception.field
            assert "TOO_LONG" == exception.error_type

    def test_undistinguish(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.comment("da2g5y6").mod.undistinguish()

    def test_unignore_reports(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.comment("da2g5y6").mod.unignore_reports()
