import pytest

from praw.exceptions import RedditAPIException
from praw.models import Comment, InlineGif, InlineImage, InlineVideo, Submission

from ... import IntegrationTest


class TestSubmission(IntegrationTest):
    @staticmethod
    def _inline_media(image_path):
        gif = InlineGif(image_path("test.gif"), "optional caption")
        image = InlineImage(image_path("test.png"), "optional caption")
        video = InlineVideo(image_path("test.mp4"), "optional caption")
        return {"gif1": gif, "image1": image, "video1": video}

    @staticmethod
    def _new_submission_instance(reddit, submission_id, return_rtjson=False):
        submission = Submission(reddit, submission_id)
        submission.add_fetch_param("rtj", "all")
        if return_rtjson:
            return submission, submission.rtjson
        return submission

    @pytest.mark.cassette_name("TestSubmission.test_award")
    def test_award(self, reddit):
        reddit.read_only = False
        award_data = Submission(reddit, "j3kyoo").award()
        assert award_data["gildings"]["gid_2"] == 1

    def test_award__not_enough_coins(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            Submission(reddit, "j3fkiw").award(
                gild_type="award_2385c499-a1fb-44ec-b9b7-d260f3dc55de"
            )
        exception = excinfo.value
        assert "INSUFFICIENT_COINS_WITH_AMOUNT" == exception.error_type

    @pytest.mark.cassette_name("TestSubmission.test_award__self_gild")
    def test_award__self_gild(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            Submission(reddit, "j3fkiw").award(
                gild_type="award_2385c499-a1fb-44ec-b9b7-d260f3dc55de"
            )
        exception = excinfo.value
        assert "SELF_GILDING_NOT_ALLOWED" == exception.error_type

    def test_clear_vote(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b536p").clear_vote()

    def test_comments(self, reddit):
        submission = Submission(reddit, "2gmzqe")
        assert len(submission.comments) == 1
        assert isinstance(submission.comments[0], Comment)
        assert isinstance(submission.comments[0].replies[0], Comment)

    def test_crosspost(self, reddit):
        reddit.read_only = False
        subreddit = pytest.placeholders.test_subreddit
        crosspost_parent = reddit.submission("6vx01b")

        submission = crosspost_parent.crosspost(subreddit)
        assert submission.author == reddit.config.username
        assert submission.title == "Test Title"
        assert submission.crosspost_parent == "t3_6vx01b"

    def test_crosspost__custom_title(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        crosspost_parent = reddit.submission("6vx01b")

        submission = crosspost_parent.crosspost(subreddit, title="my title")
        assert submission.author == reddit.config.username
        assert submission.title == "my title"
        assert submission.crosspost_parent == "t3_6vx01b"

    def test_crosspost__flair(self, reddit):
        flair_id = "2d2321ca-9205-11e9-a847-0e9f3cfadcac"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        reddit.read_only = False
        subreddit = pytest.placeholders.test_subreddit
        crosspost_parent = reddit.submission("6vx01b")

        submission = crosspost_parent.crosspost(
            subreddit, flair_id=flair_id, flair_text=flair_text
        )
        assert submission.link_flair_css_class == flair_class
        assert submission.link_flair_text == flair_text
        assert submission.crosspost_parent == "t3_6vx01b"

    def test_crosspost__nsfw(self, reddit):
        reddit.read_only = False
        subreddit = pytest.placeholders.test_subreddit
        crosspost_parent = reddit.submission("6vx01b")

        submission = crosspost_parent.crosspost(subreddit, nsfw=True)
        assert submission.over_18 is True
        assert submission.crosspost_parent == "t3_6vx01b"

    def test_crosspost__spoiler(self, reddit):
        reddit.read_only = False
        subreddit = pytest.placeholders.test_subreddit
        crosspost_parent = reddit.submission("6vx01b")

        submission = crosspost_parent.crosspost(subreddit, spoiler=True)
        assert submission.spoiler is True
        assert submission.crosspost_parent == "t3_6vx01b"

    def test_crosspost__subreddit_object(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        crosspost_parent = reddit.submission("6vx01b")

        submission = crosspost_parent.crosspost(subreddit)
        assert submission.author == reddit.config.username
        assert submission.title == "Test Title"
        assert submission.crosspost_parent == "t3_6vx01b"

    def test_delete(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4b1tfm")
        submission.delete()
        assert submission.author is None
        assert submission.selftext == "[deleted]"

    def test_disable_inbox_replies(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "6ckfdz")
        submission.disable_inbox_replies()

    def test_downvote(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b536p").downvote()

    def test_duplicates(self, reddit):
        submission = Submission(reddit, "avj2v")
        assert len(list(submission.duplicates())) > 0

    def test_edit(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4b1tfm")
        submission.edit("New text")
        assert submission.selftext == "New text"

    def test_edit__existing_and_new_inline_media(self, image_path, reddit):
        reddit.read_only = False
        inline_media = self._inline_media(image_path)
        submission, original_rtjson = self._new_submission_instance(
            reddit, "mcqjl8", True
        )
        submission2 = self._new_submission_instance(reddit, "mcqjl8")
        new_selftext = (
            "\n\nNew text with a gif {gif1} an image {image1} and a video {video1}"
            " inline"
        )
        submission._edit_experimental(
            submission.selftext + new_selftext,
            inline_media=inline_media,
            preserve_inline_media=True,
        )
        added_rtjson = submission2.subreddit._convert_to_fancypants(
            new_selftext.format(**inline_media)
        )
        assert (
            original_rtjson["document"] + added_rtjson["document"]
        ) == submission2.rtjson["document"]

    def test_edit__existing_inline_media(self, reddit):
        reddit.read_only = False
        submission, original_rtjson = self._new_submission_instance(
            reddit, "mcqjl8", True
        )
        submission2 = self._new_submission_instance(reddit, "mcqjl8")
        assert not submission2._fetched
        submission._edit_experimental(submission.selftext, preserve_inline_media=True)
        assert original_rtjson == submission2.rtjson

    def test_edit__experimental(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "mcqjl8")
        submission._edit_experimental("New text")
        assert submission.selftext == "New text"

    def test_edit__new_inline_media(self, image_path, reddit):
        reddit.read_only = False
        inline_media = self._inline_media(image_path)
        submission, original_rtjson = self._new_submission_instance(
            reddit, "mcqjl8", True
        )
        submission2 = self._new_submission_instance(reddit, "mcqjl8")
        additional_selftext = (
            "\n\nNew Text with a gif {gif1} an image {image1} and a video {video1}"
            " inline"
        )
        submission._edit_experimental(
            submission.selftext + additional_selftext,
            inline_media=inline_media,
        )
        added_rtjson = submission2.subreddit._convert_to_fancypants(
            additional_selftext.format(**inline_media)
        )
        assert (
            original_rtjson["document"] + added_rtjson["document"]
        ) == submission2.rtjson["document"]

    def test_edit_invalid(self, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        submission = Submission(reddit, "eippcc")
        with pytest.raises(RedditAPIException):
            submission.edit("rewtwert")

    def test_enable_inbox_replies(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "6ckfdz")
        submission.enable_inbox_replies()

    @pytest.mark.cassette_name("TestSubmission.test_award")
    def test_gild(self, reddit):
        reddit.read_only = False
        award_data = Submission(reddit, "j3kyoo").gild()
        assert award_data["gildings"]["gid_2"] == 1

    def test_gilded(self, reddit):
        assert 1 == Submission(reddit, "2gmzqe").gilded

    def test_hide(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b1tfm").hide()

    def test_hide_multiple(self, reddit):
        reddit.read_only = False
        submissions = [
            Submission(reddit, "fewoh"),
            Submission(reddit, "c625v"),
        ]
        Submission(reddit, "1eipl7").hide(other_submissions=submissions)

    def test_hide_multiple_in_batches(self, reddit):
        reddit.read_only = False
        submissions = list(reddit.subreddit("popular").hot(limit=100))
        assert len(submissions) == 100
        submissions[0].hide(other_submissions=submissions[1:])

    def test_invalid_attribute(self, reddit):
        submission = Submission(reddit, "2gmzqe")
        with pytest.raises(AttributeError) as excinfo:
            submission.invalid_attribute
        assert excinfo.value.args[0] == (
            "'Submission' object has no attribute 'invalid_attribute'"
        )

    def test_mark_visited(self, reddit):
        reddit.read_only = False
        Submission(reddit, "8s529q").mark_visited()

    def test_reply(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4b1tfm")
        comment = submission.reply(body="Test reply")
        assert comment.author == reddit.config.username
        assert comment.body == "Test reply"
        assert comment.parent_id == submission.fullname

    def test_reply__none(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "ah19vv")
        reply = submission.reply(body="TEST")
        assert reply is None

    def test_report(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b536h").report("praw")

    def test_save(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b536p").save()

    def test_unhide(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b1tfm").unhide()

    def test_unhide_multiple(self, reddit):
        reddit.read_only = False
        submissions = [
            Submission(reddit, "fewoh"),
            Submission(reddit, "c625v"),
        ]
        Submission(reddit, "1eipl7").unhide(other_submissions=submissions)

    def test_unhide_multiple_in_batches(self, reddit):
        reddit.read_only = False
        submissions = list(reddit.subreddit("popular").hot(limit=100))
        assert len(submissions) == 100
        submissions[0].unhide(other_submissions=submissions[1:])

    def test_unsave(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b536p").unsave()

    def test_upvote(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4b536p").upvote()


class TestSubmissionFlair(IntegrationTest):
    def test_choices(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4t4t2h")
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

    def test_select(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4t4t2h")
        submission.flair.select("16cabd0a-a68d-11e5-8349-0e8ff96e6679")


class TestSubmissionModeration(IntegrationTest):
    def test_add_removal_reason(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "e3oo6a")
        submission.mod.remove()
        submission.mod._add_removal_reason(mod_note="Foobar", reason_id="110nhral8vygf")

    def test_add_removal_reason_without_id(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "e3om6k")
        submission.mod.remove()
        submission.mod._add_removal_reason(mod_note="Foobar")

    def test_add_removal_reason_without_id_or_note(self, reddit):
        reddit.read_only = False
        with pytest.raises(ValueError) as excinfo:
            submission = Submission(reddit, "e4ds11")
            submission.mod.remove()
            submission.mod._add_removal_reason()
        assert excinfo.value.args[0].startswith("mod_note cannot be blank")

    def test_approve(self, reddit):
        reddit.read_only = False
        reddit.submission("4b536h").mod.approve()

    def test_contest_mode(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4s2idz")
        submission.mod.contest_mode()

    def test_contest_mode__disable(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "4s2idz")
        submission.mod.contest_mode(state=False)

    def test_distinguish(self, reddit):
        reddit.read_only = False
        reddit.submission("4b536h").mod.distinguish()

    def test_flair(self, reddit):
        reddit.read_only = False
        reddit.submission("4b536p").mod.flair(text="submission flair")

    def test_flair_all(self, reddit):
        reddit.read_only = False
        reddit.submission("eh9xy1").mod.flair(
            text="submission flair",
            css_class="submission flair",
            flair_template_id="0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
        )

    def test_flair_just_css_class(self, reddit):
        reddit.read_only = False
        reddit.submission("eh9xy1").mod.flair(css_class="submission flair")

    def test_flair_just_template_id(self, reddit):
        reddit.read_only = False
        reddit.submission("eh9xy1").mod.flair(
            flair_template_id="0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d"
        )

    def test_flair_template_id(self, reddit):
        reddit.read_only = False
        reddit.submission("eh9xy1").mod.flair(
            text="submission flair",
            flair_template_id="0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
        )

    def test_flair_text_and_css_class(self, reddit):
        reddit.read_only = False
        reddit.submission("eh9xy1").mod.flair(
            text="submission flair", css_class="submission flair"
        )

    def test_flair_text_only(self, reddit):
        reddit.read_only = False
        reddit.submission("eh9xy1").mod.flair(text="submission flair")

    def test_ignore_reports(self, reddit):
        reddit.read_only = False
        reddit.submission("31ybt2").mod.ignore_reports()

    def test_lock(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.lock()

    def test_notes(self, reddit):
        reddit.read_only = False
        submission = reddit.submission("uflrmv")
        note = submission.mod.create_note(label="HELPFUL_USER", note="test note")
        notes = list(submission.mod.author_notes())
        assert note in notes
        assert notes[notes.index(note)].user == submission.author

    def test_nsfw(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.nsfw()

    def test_remove(self, reddit):
        reddit.read_only = False
        reddit.submission("4b536h").mod.remove(spam=True)

    def test_remove_with_reason_id(self, reddit):
        reddit.read_only = False
        reddit.submission("e3op46").mod.remove(reason_id="110nhral8vygf")

    def test_send_removal_message(self, reddit):
        reddit.read_only = False
        submission = reddit.submission("aezo6s")
        mod = submission.mod
        mod.remove()
        message = "message"
        res = [
            mod.send_removal_message(message=type, title="title", type=message)
            for type in ("public", "private", "private_exposed")
        ]
        assert isinstance(res[0], Comment)
        assert res[0].parent_id == f"t3_{submission.id}"
        assert res[0].stickied
        assert res[0].body == message
        assert res[1] is None
        assert res[2] is None

    def test_set_original_content(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "dueqm6")
        assert not submission.is_original_content
        submission.mod.set_original_content()
        submission = Submission(reddit, "dueqm6")
        assert submission.is_original_content

    def test_sfw(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.sfw()

    def test_spoiler(self, reddit):
        reddit.read_only = False
        Submission(reddit, "5ouli3").mod.spoiler()

    def test_sticky(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.sticky()

    def test_sticky__ignore_conflicts(self, reddit):
        reddit.read_only = False
        Submission(reddit, "f1iczt").mod.sticky(bottom=False)
        Submission(reddit, "f1iczt").mod.sticky(bottom=False)

    def test_sticky__remove(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.sticky(state=False)

    def test_sticky__top(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.sticky(bottom=False)

    def test_suggested_sort(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.suggested_sort(sort="random")

    def test_suggested_sort__clear(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.suggested_sort(sort="blank")

    def test_undistinguish(self, reddit):
        reddit.read_only = False
        reddit.submission("4b536h").mod.undistinguish()

    def test_unignore_reports(self, reddit):
        reddit.read_only = False
        reddit.submission("31ybt2").mod.unignore_reports()

    def test_unlock(self, reddit):
        reddit.read_only = False
        Submission(reddit, "4s2idz").mod.unlock()

    def test_unset_original_content(self, reddit):
        reddit.read_only = False
        submission = Submission(reddit, "duig7f")
        assert submission.is_original_content
        submission.mod.unset_original_content()
        submission = Submission(reddit, "duig7f")
        assert not submission.is_original_content

    def test_unspoiler(self, reddit):
        reddit.read_only = False
        Submission(reddit, "5ouli3").mod.unspoiler()

    def test_update_crowd_control_level(self, reddit):
        reddit.read_only = False
        submission = reddit.submission("4s2idz")
        submission.mod.update_crowd_control_level(2)
        modlog = next(
            reddit.subreddit("mod").mod.log(
                action="adjust_post_crowd_control_level", limit=1
            )
        )
        assert modlog.action == "adjust_post_crowd_control_level"
        assert modlog.details == "medium"
        assert modlog.target_fullname == submission.fullname
