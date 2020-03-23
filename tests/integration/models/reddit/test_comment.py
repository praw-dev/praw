import mock
import pytest

from praw.exceptions import ClientException, PRAWException, RedditAPIException
from praw.models import Comment, Submission

from ... import IntegrationTest


class TestComment(IntegrationTest):
    def test_attributes(self):
        with self.recorder.use_cassette("TestComment.test_attributes"):
            comment = Comment(self.reddit, "cklhv0f")
            assert comment.author == "bboe"
            assert comment.body.startswith("Yes it does.")
            assert not comment.is_root
            assert comment.submission == "2gmzqe"

    @mock.patch("time.sleep", return_value=None)
    def test_block(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_block"):
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
        with self.recorder.use_cassette("TestComment.test_clear_vote"):
            Comment(self.reddit, "d1680wu").clear_vote()

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_delete"):
            comment = Comment(self.reddit, "d1616q2")
            comment.delete()
            assert comment.author is None
            assert comment.body == "[deleted]"

    def test_disable_inbox_replies(self):
        self.reddit.read_only = False
        comment = Comment(self.reddit, "dcc9snh")
        with self.recorder.use_cassette(
            "TestComment.test_disable_inbox_replies"
        ):
            comment.disable_inbox_replies()

    def test_downvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_downvote"):
            Comment(self.reddit, "d1680wu").downvote()

    @mock.patch("time.sleep", return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_edit"):
            comment = Comment(self.reddit, "d1616q2")
            comment.edit("New text")
            assert comment.body == "New text"

    def test_enable_inbox_replies(self):
        self.reddit.read_only = False
        comment = Comment(self.reddit, "dcc9snh")
        with self.recorder.use_cassette(
            "TestComment.test_enable_inbox_replies"
        ):
            comment.enable_inbox_replies()

    def test_gild__no_creddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_gild__no_creddits"):
            with pytest.raises(RedditAPIException) as excinfo:
                Comment(self.reddit, "d1616q2").gild()
            exception = excinfo.value
            assert "INSUFFICIENT_CREDDITS" == exception.error_type

    def test_invalid(self):
        with self.recorder.use_cassette("TestComment.test_invalid"):
            with pytest.raises(PRAWException) as excinfo:
                Comment(self.reddit, "0").body
            assert excinfo.value.args[0].startswith(
                "No data returned for comment"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_mark_read"):
            comment = next(self.reddit.inbox.unread())
            assert isinstance(comment, Comment)
            comment.mark_read()

    @mock.patch("time.sleep", return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_mark_unread"):
            comment = next(self.reddit.inbox.comment_replies())
            comment.mark_unread()

    def test_parent__comment(self):
        comment = Comment(self.reddit, "cklhv0f")
        with self.recorder.use_cassette("TestComment.test_parent__comment"):
            parent = comment.parent()
            parent.refresh()
            assert comment in parent.replies
        assert isinstance(parent, Comment)
        assert parent.fullname == comment.parent_id

    def test_parent__chain(self):
        comment = Comment(self.reddit, "dkk4qjd")
        counter = 0
        with self.recorder.use_cassette("TestComment.test_parent__chain"):
            comment.refresh()
            parent = comment.parent()
            while parent != comment.submission:
                if counter % 9 == 0:
                    parent.refresh()
                counter += 1
                parent = parent.parent()

    def test_parent__comment_from_forest(self):
        submission = self.reddit.submission("2gmzqe")
        with self.recorder.use_cassette(
            "TestComment.test_parent__comment_from_forest"
        ):
            comment = submission.comments[0].replies[0]
        parent = comment.parent()
        assert comment in parent.replies
        assert isinstance(parent, Comment)
        assert parent.fullname == comment.parent_id

    @mock.patch("time.sleep", return_value=None)
    def test_parent__from_replies(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.parent__from_replies"):
            comment = next(self.reddit.inbox.comment_replies())
        parent = comment.parent()
        assert isinstance(parent, Comment)
        assert parent.fullname == comment.parent_id

    def test_parent__submission(self):
        comment = Comment(self.reddit, "cklfmye")
        with self.recorder.use_cassette("TestComment.test_parent__submission"):
            parent = comment.parent()
            assert comment in parent.comments
        assert isinstance(parent, Submission)
        assert parent.fullname == comment.parent_id

    def test_refresh(self):
        comment = Comment(self.reddit, "d81vwef")
        with self.recorder.use_cassette("TestComment.test_refresh"):
            assert len(comment.replies) == 0
            comment.refresh()
            assert len(comment.replies) > 0

    def test_refresh__raises_exception(self):
        with self.recorder.use_cassette(
            "TestComment.test_refresh__raises_exception"
        ):
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, "d81vwef").refresh()
        assert (
            "This comment does not appear to be in the comment tree",
        ) == excinfo.value.args

    def test_refresh__twice(self):
        with self.recorder.use_cassette("TestComment.test_refresh__twice"):
            Comment(self.reddit, "d81vwef").refresh().refresh()

    def test_refresh__deleted_comment(self):
        with self.recorder.use_cassette(
            "TestComment.test_refresh__deleted_comment"
        ):
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, "d7ltvl0").refresh()
        assert (
            "This comment does not appear to be in the comment tree",
        ) == excinfo.value.args

    def test_refresh__removed_comment(self):
        with self.recorder.use_cassette(
            "TestComment.test_refresh__removed_comment"
        ):
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, "dma3mi5").refresh()
        assert (
            "This comment does not appear to be in the comment tree",
        ) == excinfo.value.args

    def test_refresh__with_reply_sort_and_limit(self):
        with self.recorder.use_cassette(
            "TestComment.test_refresh__with_reply_sort_and_limit"
        ):
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
        with self.recorder.use_cassette("TestComment.test_reply"):
            parent_comment = Comment(self.reddit, "d1616q2")
            comment = parent_comment.reply("Comment reply")
            assert comment.author == self.reddit.config.username
            assert comment.body == "Comment reply"
            assert not comment.is_root
            assert comment.parent_id == parent_comment.fullname

    def test_reply__none(self):
        self.reddit.read_only = False
        comment = Comment(self.reddit, "eear2ml")
        with self.recorder.use_cassette("TestComment.test_reply__none"):
            reply = comment.reply("TEST")
        assert reply is None

    def test_report(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_report"):
            Comment(self.reddit, "d0335z3").report("custom")

    def test_report_admin(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_report_admin"):
            self.reddit.comment("fl2c5ax").report_admin(
                "Anti-LGBT content",
                explanation="This is a transphobic comment",
            )

    def test_save(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_save"):
            Comment(self.reddit, "d1680wu").save("foo")

    def test_unsave(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_unsave"):
            Comment(self.reddit, "d1680wu").unsave()

    def test_upvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestComment.test_upvote"):
            Comment(self.reddit, "d1680wu").upvote()


class TestCommentModeration(IntegrationTest):
    def test_approve(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestCommentModeration.test_approve"):
            Comment(self.reddit, "da2g5y6").mod.approve()

    def test_distinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_distinguish"
        ):
            Comment(self.reddit, "da2g5y6").mod.distinguish()

    @mock.patch("time.sleep", return_value=None)
    def test_distinguish__sticky(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_distinguish__sticky"
        ):
            Comment(self.reddit, "da2g5y6").mod.distinguish(sticky=True)

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_ignore_reports"
        ):
            self.reddit.comment("da2g5y6").mod.ignore_reports()

    def test_lock(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestCommentModeration.test_lock"):
            Comment(self.reddit, "da2g6ne").mod.lock()

    def test_remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestCommentModeration.test_remove"):
            self.reddit.comment("da2g5y6").mod.remove(spam=True)

    @mock.patch("time.sleep", return_value=None)
    def test_remove_with_reason_id(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_remove_with_reason_id"
        ):
            self.reddit.comment("f3dm3b7").mod.remove(
                reason_id="110nhral8vygf"
            )

    def test_show(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestCommentModeration.test_show"):
            self.reddit.comment("fjyyrv6").mod.show()

    def test_unlock(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestCommentModeration.test_unlock"):
            Comment(self.reddit, "da2g6ne").mod.unlock()

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_add_removal_reason"
        ):
            comment = self.reddit.comment("f98ukt5")
            comment.mod.remove()
            comment.mod._add_removal_reason(
                mod_note="Blah", reason_id="110nhral8vygf"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason_without_id(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_add_removal_reason_without_id"
        ):
            comment = self.reddit.comment("f98ugot")
            comment.mod.remove()
            comment.mod._add_removal_reason(mod_note="Test")

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason_without_id_or_note(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_add_removal_reason_invalid"
        ):
            with pytest.raises(ValueError) as excinfo:
                comment = self.reddit.comment("f9974ce")
                comment.mod.remove()
                comment.mod._add_removal_reason()
            assert excinfo.value.args[0].startswith("mod_note cannot be blank")

    @mock.patch("time.sleep", return_value=None)
    def test_send_removal_message(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_send_removal_message"
        ):
            comment = self.reddit.comment("edu698v")
            mod = comment.mod
            mod.remove()
            message = "message"
            res = [
                mod.send_removal_message(message, "title", type)
                for type in ("public", "private", "private_exposed")
            ]
            assert isinstance(res[0], Comment)
            assert res[0].parent_id == "t1_" + comment.id
            assert res[0].body == message
            assert res[1] is None
            assert res[2] is None

    @mock.patch("time.sleep", return_value=None)
    def test_send_removal_message__error(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_send_removal_message__error"
        ):
            comment = self.reddit.comment("fkmrn4a")
            comment.mod.remove()
            with pytest.raises(RedditAPIException) as excinfo:
                comment.mod.send_removal_message("message", "a" * 51)
            exception = excinfo.value
            assert "title" == exception.field
            assert "TOO_LONG" == exception.error_type

    def test_undistinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_undistinguish"
        ):
            self.reddit.comment("da2g5y6").mod.undistinguish()

    def test_unignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestCommentModeration.test_unignore_reports"
        ):
            self.reddit.comment("da2g5y6").mod.unignore_reports()
