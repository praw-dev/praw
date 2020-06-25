from unittest import mock

import pytest

from praw.exceptions import RedditAPIException
from praw.models import Comment, Submission

from ... import IntegrationTest


class TestSubmission(IntegrationTest):
    def test_comments(self):
        with self.use_cassette():
            submission = Submission(self.reddit, "2gmzqe")
            assert len(submission.comments) == 1
            assert isinstance(submission.comments[0], Comment)
            assert isinstance(submission.comments[0].replies[0], Comment)

    def test_clear_vote(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b536p").clear_vote()

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4b1tfm")
            submission.delete()
            assert submission.author is None
            assert submission.selftext == "[deleted]"

    def test_disable_inbox_replies(self):
        self.reddit.read_only = False
        submission = Submission(self.reddit, "6ckfdz")
        with self.use_cassette():
            submission.disable_inbox_replies()

    def test_downvote(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b536p").downvote()

    def test_duplicates(self):
        with self.use_cassette():
            submission = Submission(self.reddit, "avj2v")
            assert len(list(submission.duplicates())) > 0

    @mock.patch("time.sleep", return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4b1tfm")
            submission.edit("New text")
            assert submission.selftext == "New text"

    @mock.patch("time.sleep", return_value=None)
    def test_edit_invalid(self, _):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            submission = Submission(self.reddit, "eippcc")
            with pytest.raises(RedditAPIException):
                submission.edit("rewtwert")

    def test_enable_inbox_replies(self):
        self.reddit.read_only = False
        submission = Submission(self.reddit, "6ckfdz")
        with self.use_cassette():
            submission.enable_inbox_replies()

    def test_award(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubmission.test_award"):
            award_data = Submission(self.reddit, "j3kyoo").award()
            assert award_data["gildings"]["gid_2"] == 1

    def test_award__not_enough_coins(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                Submission(self.reddit, "j3fkiw").award(
                    gild_type="award_2385c499-a1fb-44ec-b9b7-d260f3dc55de"
                )
            exception = excinfo.value
            assert "INSUFFICIENT_COINS_WITH_AMOUNT" == exception.error_type

    def test_award__self_gild(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubmission.test_award__self_gild"):
            with pytest.raises(RedditAPIException) as excinfo:
                Submission(self.reddit, "j3fkiw").award(
                    gild_type="award_2385c499-a1fb-44ec-b9b7-d260f3dc55de"
                )
            exception = excinfo.value
            assert "SELF_GILDING_NOT_ALLOWED" == exception.error_type

    def test_gild(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubmission.test_award"):
            award_data = Submission(self.reddit, "j3kyoo").gild()
            assert award_data["gildings"]["gid_2"] == 1

    def test_gilded(self):
        with self.use_cassette():
            assert 1 == Submission(self.reddit, "2gmzqe").gilded

    def test_hide(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b1tfm").hide()

    def test_hide_multiple(self):
        self.reddit.read_only = False
        submissions = [
            Submission(self.reddit, "fewoh"),
            Submission(self.reddit, "c625v"),
        ]
        with self.use_cassette():
            Submission(self.reddit, "1eipl7").hide(submissions)

    @mock.patch("time.sleep", return_value=None)
    def test_hide_multiple_in_batches(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submissions = list(self.reddit.subreddit("popular").hot(limit=100))
            assert len(submissions) == 100
            submissions[0].hide(submissions[1:])

    def test_invalid_attribute(self):
        with self.use_cassette():
            submission = Submission(self.reddit, "2gmzqe")
            with pytest.raises(AttributeError) as excinfo:
                submission.invalid_attribute
        assert excinfo.value.args[0] == (
            "'Submission' object has no attribute 'invalid_attribute'"
        )

    def test_reply(self):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4b1tfm")
            comment = submission.reply("Test reply")
            assert comment.author == self.reddit.config.username
            assert comment.body == "Test reply"
            assert comment.parent_id == submission.fullname

    def test_reply__none(self):
        self.reddit.read_only = False
        submission = Submission(self.reddit, "ah19vv")
        with self.use_cassette():
            reply = submission.reply("TEST")
        assert reply is None

    def test_report(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b536h").report("praw")

    def test_save(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b536p").save()

    def test_mark_visited(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "8s529q").mark_visited()

    def test_unhide(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b1tfm").unhide()

    def test_unhide_multiple(self):
        self.reddit.read_only = False
        submissions = [
            Submission(self.reddit, "fewoh"),
            Submission(self.reddit, "c625v"),
        ]
        with self.use_cassette():
            Submission(self.reddit, "1eipl7").unhide(submissions)

    @mock.patch("time.sleep", return_value=None)
    def test_unhide_multiple_in_batches(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submissions = list(self.reddit.subreddit("popular").hot(limit=100))
            assert len(submissions) == 100
            submissions[0].unhide(submissions[1:])

    def test_unsave(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b536p").unsave()

    def test_upvote(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4b536p").upvote()

    @mock.patch("time.sleep", return_value=None)
    def test_crosspost(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = pytest.placeholders.test_subreddit
            crosspost_parent = self.reddit.submission(id="6vx01b")

            submission = crosspost_parent.crosspost(subreddit)
            assert submission.author == self.reddit.config.username
            assert submission.title == "Test Title"
            assert submission.crosspost_parent == "t3_6vx01b"

    @mock.patch("time.sleep", return_value=None)
    def test_crosspost__subreddit_object(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            crosspost_parent = self.reddit.submission(id="6vx01b")

            submission = crosspost_parent.crosspost(subreddit)
            assert submission.author == self.reddit.config.username
            assert submission.title == "Test Title"
            assert submission.crosspost_parent == "t3_6vx01b"

    @mock.patch("time.sleep", return_value=None)
    def test_crosspost__custom_title(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            crosspost_parent = self.reddit.submission(id="6vx01b")

            submission = crosspost_parent.crosspost(subreddit, "my title")
            assert submission.author == self.reddit.config.username
            assert submission.title == "my title"
            assert submission.crosspost_parent == "t3_6vx01b"

    @mock.patch("time.sleep", return_value=None)
    def test_crosspost__flair(self, _):
        flair_id = "2d2321ca-9205-11e9-a847-0e9f3cfadcac"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = pytest.placeholders.test_subreddit
            crosspost_parent = self.reddit.submission(id="6vx01b")

            submission = crosspost_parent.crosspost(
                subreddit, flair_id=flair_id, flair_text=flair_text
            )
            assert submission.link_flair_css_class == flair_class
            assert submission.link_flair_text == flair_text
            assert submission.crosspost_parent == "t3_6vx01b"

    @mock.patch("time.sleep", return_value=None)
    def test_crosspost__nsfw(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = pytest.placeholders.test_subreddit
            crosspost_parent = self.reddit.submission(id="6vx01b")

            submission = crosspost_parent.crosspost(subreddit, nsfw=True)
            assert submission.over_18 is True
            assert submission.crosspost_parent == "t3_6vx01b"

    @mock.patch("time.sleep", return_value=None)
    def test_crosspost__spoiler(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = pytest.placeholders.test_subreddit
            crosspost_parent = self.reddit.submission(id="6vx01b")

            submission = crosspost_parent.crosspost(subreddit, spoiler=True)
            assert submission.spoiler is True
            assert submission.crosspost_parent == "t3_6vx01b"


class TestSubmissionFlair(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_choices(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4t4t2h")
            expected = [
                {
                    "flair_text": "SATISFIED",
                    "flair_template_id": "680f43b8-1fec-11e3-80d1-12313b0b80bc",  # noqa:E501
                    "flair_text_editable": False,
                    "flair_position": "left",
                    "flair_css_class": "",
                },
                {
                    "flair_text": "STATS",
                    "flair_template_id": "16cabd0a-a68d-11e5-8349-0e8ff96e6679",  # noqa:E501
                    "flair_text_editable": False,
                    "flair_position": "left",
                    "flair_css_class": "",
                },
            ]
            assert expected == submission.flair.choices()

    @mock.patch("time.sleep", return_value=None)
    def test_select(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4t4t2h")
            submission.flair.select("16cabd0a-a68d-11e5-8349-0e8ff96e6679")


class TestSubmissionModeration(IntegrationTest):
    def test_approve(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("4b536h").mod.approve()

    def test_contest_mode(self):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4s2idz")
            submission.mod.contest_mode()

    def test_contest_mode__disable(self):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "4s2idz")
            submission.mod.contest_mode(state=False)

    @mock.patch("time.sleep", return_value=None)
    def test_flair(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("4b536p").mod.flair("submission flair")

    @mock.patch("time.sleep", return_value=None)
    def test_flair_template_id(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("eh9xy1").mod.flair(
                "submission flair",
                flair_template_id="0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
            )

    @mock.patch("time.sleep", return_value=None)
    def test_flair_text_only(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("eh9xy1").mod.flair("submission flair")

    @mock.patch("time.sleep", return_value=None)
    def test_flair_text_and_css_class(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("eh9xy1").mod.flair(
                "submission flair", css_class="submission flair"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_flair_all(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("eh9xy1").mod.flair(
                "submission flair",
                css_class="submission flair",
                flair_template_id="0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
            )

    @mock.patch("time.sleep", return_value=None)
    def test_flair_just_template_id(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("eh9xy1").mod.flair(
                flair_template_id="0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_flair_just_css_class(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("eh9xy1").mod.flair(css_class="submission flair")

    def test_distinguish(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("4b536h").mod.distinguish()

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("31ybt2").mod.ignore_reports()

    def test_nsfw(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.nsfw()

    def test_lock(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.lock()

    def test_remove(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("4b536h").mod.remove(spam=True)

    @mock.patch("time.sleep", return_value=None)
    def test_remove_with_reason_id(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("e3op46").mod.remove(reason_id="110nhral8vygf")

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "e3oo6a")
            submission.mod.remove()
            submission.mod._add_removal_reason(
                mod_note="Foobar", reason_id="110nhral8vygf"
            )

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason_without_id(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "e3om6k")
            submission.mod.remove()
            submission.mod._add_removal_reason(mod_note="Foobar")

    @mock.patch("time.sleep", return_value=None)
    def test_add_removal_reason_without_id_or_note(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(ValueError) as excinfo:
                submission = Submission(self.reddit, "e4ds11")
                submission.mod.remove()
                submission.mod._add_removal_reason()
            assert excinfo.value.args[0].startswith("mod_note cannot be blank")

    @mock.patch("time.sleep", return_value=None)
    def test_send_removal_message(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = self.reddit.submission("aezo6s")
            mod = submission.mod
            mod.remove()
            message = "message"
            res = [
                mod.send_removal_message(type, "title", message)
                for type in ("public", "private", "private_exposed")
            ]
            assert isinstance(res[0], Comment)
            assert res[0].parent_id == f"t3_{submission.id}"
            assert res[0].stickied
            assert res[0].body == message
            assert res[1] is None
            assert res[2] is None

    @mock.patch("time.sleep", return_value=None)
    def test_set_original_content(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "dueqm6")
            assert not submission.is_original_content
            submission.mod.set_original_content()
            submission = Submission(self.reddit, "dueqm6")
            assert submission.is_original_content

    def test_sfw(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.sfw()

    def test_spoiler(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "5ouli3").mod.spoiler()

    def test_sticky(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.sticky()

    def test_sticky__remove(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.sticky(state=False)

    def test_sticky__top(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.sticky(bottom=False)

    @mock.patch("time.sleep", return_value=None)
    def test_sticky__ignore_conflicts(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "f1iczt").mod.sticky(bottom=False)
            Submission(self.reddit, "f1iczt").mod.sticky(bottom=False)

    def test_suggested_sort(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.suggested_sort(sort="random")

    def test_suggested_sort__clear(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.suggested_sort(sort="blank")

    def test_undistinguish(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("4b536h").mod.undistinguish()

    def test_unignore_reports(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.submission("31ybt2").mod.unignore_reports()

    def test_unlock(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "4s2idz").mod.unlock()

    @mock.patch("time.sleep", return_value=None)
    def test_unset_original_content(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            submission = Submission(self.reddit, "duig7f")
            assert submission.is_original_content
            submission.mod.unset_original_content()
            submission = Submission(self.reddit, "duig7f")
            assert not submission.is_original_content

    def test_unspoiler(self):
        self.reddit.read_only = False
        with self.use_cassette():
            Submission(self.reddit, "5ouli3").mod.unspoiler()
