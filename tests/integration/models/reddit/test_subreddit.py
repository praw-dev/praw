"""Test praw.models.subreddit."""
import socket
from json import dumps
from unittest import mock
from unittest.mock import MagicMock

import pytest
import requests
import websocket
from prawcore import BadRequest, Forbidden, NotFound, RequestException, TooLarge

from praw.const import PNG_HEADER
from praw.exceptions import (
    ClientException,
    InvalidFlairTemplateID,
    RedditAPIException,
    TooLargeMediaException,
    WebSocketException,
)
from praw.models import (
    Comment,
    InlineGif,
    InlineImage,
    InlineVideo,
    ListingGenerator,
    ModAction,
    ModmailAction,
    ModmailConversation,
    ModmailMessage,
    Redditor,
    Stylesheet,
    Submission,
    Subreddit,
    SubredditMessage,
    WikiPage,
)

from ... import IntegrationTest


class TestSubredditFilters(IntegrationTest):
    def test__iter__all(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("all")
        filters = list(subreddit.filters)
        assert len(filters) > 0
        assert all(isinstance(x, Subreddit) for x in filters)

    def test__iter__mod(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("mod")
        filters = list(subreddit.filters)
        assert len(filters) > 0
        assert all(isinstance(x, Subreddit) for x in filters)

    def test_add(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("all")
        subreddit.filters.add("redditdev")

    def test_add__non_special(self, reddit):
        reddit.read_only = False
        with pytest.raises(NotFound):
            reddit.subreddit("redditdev").filters.add("redditdev")

    @pytest.mark.cassette_name("TestSubredditFilters.test_add")
    def test_add__subreddit_model(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("all")
        subreddit.filters.add(reddit.subreddit("redditdev"))

    def test_remove(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("mod")
        subreddit.filters.remove("redditdev")

    def test_remove__non_special(self, reddit):
        reddit.read_only = False
        with pytest.raises(NotFound):
            reddit.subreddit("redditdev").filters.remove("redditdev")

    @pytest.mark.cassette_name("TestSubredditFilters.test_remove")
    def test_remove__subreddit_model(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("mod")
        subreddit.filters.remove(reddit.subreddit("redditdev"))


class TestSubredditFlair(IntegrationTest):
    REDDITOR = pytest.placeholders.username

    def test__call(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        mapping = subreddit.flair()
        assert len(list(mapping)) > 0
        assert all(isinstance(x["user"], Redditor) for x in mapping)

    def test__call__user_filter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        mapping = subreddit.flair(redditor=self.REDDITOR)
        assert len(list(mapping)) == 1

    def test_configure(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.configure(
            position=None,
            self_assign=True,
            link_position=None,
            link_self_assign=True,
        )

    def test_configure__defaults(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.configure()

    def test_delete(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.delete(pytest.placeholders.username)

    def test_delete_all(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.flair.delete_all()
        assert len(response) > 100
        assert all("removed" in x["status"] for x in response)

    def test_set__flair_id(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(pytest.placeholders.username)
        flair = "11c32eee-1482-11e9-bfc0-0efc81a5e8e8"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.set(redditor, flair_template_id=flair, text="redditor flair")

    def test_set__flair_id_default_text(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(pytest.placeholders.username)
        flair = "11c32eee-1482-11e9-bfc0-0efc81a5e8e8"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.set(redditor, flair_template_id=flair)

    def test_set__redditor(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(pytest.placeholders.username)
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.set(redditor, text="redditor flair")

    def test_set__redditor_css_only(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.set(pytest.placeholders.username, css_class="some class")

    def test_set__redditor_string(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.set(
            pytest.placeholders.username, css_class="some class", text="new flair"
        )

    def test_update(self, reddit):
        reddit.read_only = False
        redditor = reddit.redditor(pytest.placeholders.username)
        flair_list = [
            redditor,
            "spez",
            {"user": "bsimpson"},
            {"user": "spladug", "flair_text": "", "flair_css_class": ""},
        ]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.flair.update(flair_list, css_class="default")
        assert all(x["ok"] for x in response)
        assert not any(x["errors"] for x in response)
        assert not any(x["warnings"] for x in response)
        assert len([x for x in response if "added" in x["status"]]) == 3
        assert len([x for x in response if "removed" in x["status"]]) == 1
        for i, name in enumerate([str(redditor), "spez", "bsimpson", "spladug"]):
            assert name in response[i]["status"]

    def test_update__comma_in_text(self, reddit):
        reddit.read_only = False
        flair_list = [
            {"user": "bsimpson"},
            {"user": "spladug", "flair_text": "a,b"},
        ]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.flair.update(flair_list, css_class="default")
        assert all(x["ok"] for x in response)

    def test_update_quotes(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.flair.update(
            [reddit.user.me()], css_class="testing", text='"testing"'
        )
        assert all(x["ok"] for x in response)
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        flair = next(subreddit.flair(reddit.user.me()))
        assert flair["flair_text"] == '"testing"'
        assert flair["flair_css_class"] == "testing"


class TestSubredditFlairTemplates(IntegrationTest):
    def test__iter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        templates = list(subreddit.flair.templates)
        assert len(templates) > 100

        for flair_template in templates:
            assert flair_template["id"]

    def test_add(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.add(
            "PRAW", background_color="#ABCDEF", css_class="myCSS"
        )

    def test_clear(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.clear()

    def test_delete(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.delete(template["id"])

    def test_update(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.update(
            template["id"],
            background_color="#00FFFF",
            css_class="myCSS",
            text="PRAW updated",
            text_color="dark",
        )

    def test_update_false(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit.flair.templates.update(template["id"], fetch=True, text_editable=True)
        subreddit.flair.templates.update(
            template["id"], fetch=True, text_editable=False
        )
        newtemplate = list(
            filter(
                lambda _template: _template["id"] == template["id"],
                subreddit.flair.templates,
            )
        )[0]
        assert newtemplate["text_editable"] is False

    def test_update_fetch(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.update(
            template["id"],
            background_color="#00FFFF",
            css_class="myCSS",
            fetch=True,
            text="PRAW updated",
            text_color="dark",
        )

    def test_update_fetch_no_css_class(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.update(
            template["id"],
            background_color="#00FFFF",
            fetch=True,
            text="PRAW updated",
            text_color="dark",
        )

    def test_update_fetch_no_text(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.update(
            template["id"],
            background_color="#00FFFF",
            css_class="myCSS",
            fetch=True,
            text_color="dark",
        )

    def test_update_fetch_no_text_or_css_class(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.templates.update(
            template["id"],
            background_color="#00FFFF",
            fetch=True,
            text_color="dark",
        )

    def test_update_fetch_only(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        template = list(subreddit.flair.templates)[0]
        subreddit.flair.templates.update(template["id"], fetch=True)
        newtemplate = list(
            filter(
                lambda _template: _template["id"] == template["id"],
                subreddit.flair.templates,
            )
        )[0]
        assert newtemplate == template

    def test_update_invalid(self, reddit):
        reddit.read_only = False
        with pytest.raises(InvalidFlairTemplateID):
            subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
            subreddit.flair.templates.update(
                "fake id",
                background_color="#00FFFF",
                css_class="myCSS",
                fetch=True,
                text="PRAW updated",
                text_color="dark",
            )


class TestSubredditLinkFlairTemplates(IntegrationTest):
    def test__iter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        templates = list(subreddit.flair.link_templates)
        assert len(templates) > 100

        for template in templates:
            assert template["id"]
            assert isinstance(template["richtext"], list)
            assert all(isinstance(item, dict) for item in template["richtext"])

    def test_add(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.link_templates.add(
            "PRAW", css_class="myCSS", text_color="light"
        )

    def test_clear(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.flair.link_templates.clear()

    def test_user_selectable(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        templates = list(subreddit.flair.link_templates.user_selectable())
        assert len(templates) >= 2

        for template in templates:
            assert template["flair_template_id"]
            assert template["flair_text"]


class TestSubredditListings(IntegrationTest):
    def test_comments(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        comments = list(subreddit.comments())
        assert len(comments) == 100

    def test_controversial(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.controversial())
        assert len(submissions) == 100

    def test_gilded(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.gilded())
        assert len(submissions) >= 50

    def test_hot(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.hot())
        assert len(submissions) == 100

    def test_new(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.new())
        assert len(submissions) == 100

    def test_random_rising(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.random_rising())
        assert len(submissions) == 100

    def test_rising(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.rising())
        assert len(submissions) == 100

    def test_top(self, reddit):
        subreddit = reddit.subreddit("askreddit")
        submissions = list(subreddit.top())
        assert len(submissions) == 100


class TestSubredditModeration(IntegrationTest):
    def test_accept_invite__no_invite(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException) as excinfo:
            subreddit.mod.accept_invite()
        assert excinfo.value.items[0].error_type == "NO_INVITE_FOUND"

    def test_edited(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.edited():
            assert isinstance(item, (Comment, Submission))
            count += 1
        assert count == 100

    def test_edited__only_comments(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.edited(only="comments"):
            assert isinstance(item, Comment)
            count += 1
        assert count == 100

    def test_edited__only_submissions(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.edited(only="submissions"):
            assert isinstance(item, Submission)
            count += 1
        assert count > 0

    def test_inbox(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit("all")
        for item in subreddit.mod.inbox():
            assert isinstance(item, SubredditMessage)
            count += 1
        assert count == 100

    def test_log(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit("mod")
        for item in subreddit.mod.log():
            assert isinstance(item, ModAction)
            count += 1
        assert count == 100

    def test_log__filters(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit("mod")
        redditor = reddit.redditor("bboe_dev")
        for item in subreddit.mod.log(action="invitemoderator", mod=redditor):
            assert isinstance(item, ModAction)
            assert item.action == "invitemoderator"
            assert isinstance(item.mod, Redditor)
            assert item.mod == "bboe_dev"
            count += 1
        assert count > 0

    def test_modqueue(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.modqueue():
            assert isinstance(item, (Comment, Submission))
            count += 1
        assert count > 0

    def test_modqueue__only_comments(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.modqueue(only="comments"):
            assert isinstance(item, Comment)
            count += 1
        assert count > 0

    def test_modqueue__only_submissions(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.modqueue(only="submissions"):
            assert isinstance(item, Submission)
            count += 1
        assert count > 0

    def test_notes(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        notes = list(subreddit.mod.notes.redditors("Watchful1", "watchful12", "spez"))
        assert len(notes) == 3
        assert notes[0].user.name.lower() == "watchful1"
        assert notes[1].user.name.lower() == "watchful12"
        assert notes[2] is None

    def test_notes_iterate(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        distinct_ids = set()
        count_notes = 0
        for note in subreddit.mod.notes.redditors("watchful12", limit=None):
            distinct_ids.add(note.id)
            count_notes += 1

        assert len(distinct_ids) == 359
        assert count_notes == 359

    def test_reports(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.reports():
            assert isinstance(item, (Comment, Submission))
            count += 1
        assert count == 100

    def test_reports__only_comments(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.reports(only="comments"):
            assert isinstance(item, Comment)
            count += 1
        assert count > 0

    def test_reports__only_submissions(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.reports(only="submissions"):
            assert isinstance(item, Submission)
            count += 1
        assert count == 100

    def test_spam(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.spam():
            assert isinstance(item, (Comment, Submission))
            count += 1
        assert count > 0

    def test_spam__only_comments(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.spam(only="comments"):
            assert isinstance(item, Comment)
            count += 1
        assert count > 0

    def test_spam__only_submissions(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.spam(only="submissions"):
            assert isinstance(item, Submission)
            count += 1
        assert count > 0

    def test_unmoderated(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for item in subreddit.mod.unmoderated():
            assert isinstance(item, (Comment, Submission))
            count += 1
        assert count > 0

    def test_unread(self, reddit):
        reddit.read_only = False
        count = 0
        subreddit = reddit.subreddit("all")
        for item in subreddit.mod.unread():
            assert isinstance(item, SubredditMessage)
            count += 1
        assert count > 0

    def test_update(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        before_settings = subreddit.mod.settings()
        new_title = f"{before_settings['title']}x"
        new_title = (
            "x"
            if (len(new_title) >= 20 and "placeholder" not in new_title)
            else new_title
        )
        subreddit.mod.update(title=new_title)
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        assert subreddit.title == new_title
        after_settings = subreddit.mod.settings()

        # Ensure that nothing has changed besides what was specified.
        before_settings["title"] = new_title
        assert before_settings == after_settings


class TestSubredditModerationStreams(IntegrationTest):
    def test_edited(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        generator = subreddit.mod.stream.edited()
        for i in range(10):
            assert isinstance(next(generator), (Comment, Submission))

    def test_log(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        generator = subreddit.mod.stream.log()
        for i in range(101):
            assert isinstance(next(generator), ModAction)

    def test_modmail_conversations(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("mod")
        generator = subreddit.mod.stream.modmail_conversations()
        for i in range(101):
            assert isinstance(next(generator), ModmailConversation)

    def test_modqueue(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        generator = subreddit.mod.stream.modqueue()
        for i in range(10):
            assert isinstance(next(generator), (Comment, Submission))

    def test_reports(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        generator = subreddit.mod.stream.reports()
        for i in range(10):
            assert isinstance(next(generator), (Comment, Submission))

    def test_spam(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        generator = subreddit.mod.stream.spam()
        for i in range(10):
            assert isinstance(next(generator), (Comment, Submission))

    def test_unmoderated(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        generator = subreddit.mod.stream.unmoderated()
        for i in range(10):
            assert isinstance(next(generator), (Comment, Submission))

    def test_unread(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("mod")
        generator = subreddit.mod.stream.unread()
        for i in range(2):
            assert isinstance(next(generator), SubredditMessage)


class TestSubredditModmail(IntegrationTest):
    def test_bulk_read(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for conversation in subreddit.modmail.bulk_read(state="new"):
            assert isinstance(conversation, ModmailConversation)

    def test_call(self, reddit):
        reddit.read_only = False
        conversation_id = "ik72"
        subreddit = reddit.subreddit("all")
        conversation = subreddit.modmail(conversation_id)
        assert isinstance(conversation.user, Redditor)
        for message in conversation.messages:
            assert isinstance(message, ModmailMessage)
        for action in conversation.mod_actions:
            assert isinstance(action, ModmailAction)

    def test_call__internal(self, reddit):
        reddit.read_only = False
        conversation_id = "nbhy"
        subreddit = reddit.subreddit("all")
        conversation = subreddit.modmail(conversation_id)
        for message in conversation.messages:
            assert isinstance(message, ModmailMessage)
        for action in conversation.mod_actions:
            assert isinstance(action, ModmailAction)

    def test_call__mark_read(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("all")
        conversation = subreddit.modmail("o7wz", mark_read=True)
        assert conversation.last_unread is None

    def test_conversations(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("all")
        conversations = subreddit.modmail.conversations()
        for conversation in conversations:
            assert isinstance(conversation, ModmailConversation)
            assert isinstance(conversation.authors[0], Redditor)

    def test_conversations__other_subreddits(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("pics")
        conversations = subreddit.modmail.conversations(
            other_subreddits=["LifeProTips"]
        )
        assert len(set(list(conversation.owner for conversation in conversations))) > 1

    def test_conversations__params(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("all")
        conversations = subreddit.modmail.conversations(state="mod")
        for conversation in conversations:
            assert conversation.is_internal

    def test_create(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        redditor = reddit.redditor(pytest.placeholders.username)
        conversation = subreddit.modmail.create(
            subject="Subject", body="Body", recipient=redditor
        )
        assert isinstance(conversation, ModmailConversation)

    def test_subreddits(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for subreddit in subreddit.modmail.subreddits():
            assert isinstance(subreddit, Subreddit)

    def test_unread_count(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        assert isinstance(subreddit.modmail.unread_count(), dict)


class TestSubredditQuarantine(IntegrationTest):
    def test_opt_in(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("ferguson")
        with pytest.raises(Forbidden):
            next(subreddit.hot())
        subreddit.quaran.opt_in()
        assert isinstance(next(subreddit.hot()), Submission)

    def test_opt_out(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit("ferguson")
        subreddit.quaran.opt_out()
        with pytest.raises(Forbidden):
            next(subreddit.hot())


class TestSubredditRelationships(IntegrationTest):
    REDDITOR = "pyapitestuser3"

    @staticmethod
    def _add_remove(base, relationship, user):
        relationship = getattr(base, relationship)
        relationship.add(user)
        relationships = list(relationship())
        assert user in relationships
        redditor = relationships[relationships.index(user)]
        assert isinstance(redditor, Redditor)
        assert hasattr(redditor, "date")
        relationship.remove(user)
        assert user not in list(relationship())

    def test_banned(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        self._add_remove(subreddit, "banned", self.REDDITOR)

    def test_banned__user_filter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        banned = subreddit.banned(redditor="pyapitestuser3")
        assert len(list(banned)) == 1

    def test_contributor(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        self._add_remove(subreddit, "contributor", self.REDDITOR)

    def test_contributor__user_filter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        contributor = subreddit.contributor(redditor="pyapitestuser3")
        assert len(list(contributor)) == 1

    def test_contributor_leave(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.contributor.leave()

    def test_moderator(self, reddit):
        reddit.read_only = False
        # Moderators can only be invited.
        # As of 2016-03-18 there is no API endpoint to get the moderator
        # invite list.
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.add(self.REDDITOR)
        assert self.REDDITOR not in subreddit.moderator()

    def test_moderator__limited_permissions(self, reddit):
        reddit.read_only = False
        # Moderators can only be invited.
        # As of 2016-03-18 there is no API endpoint to get the moderator
        # invite list.
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.add(self.REDDITOR, permissions=["access", "wiki"])
        assert self.REDDITOR not in subreddit.moderator()

    def test_moderator__user_filter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        moderator = subreddit.moderator(redditor="pyapitestuser3")
        assert len(moderator) == 1
        assert "mod_permissions" in moderator[0].__dict__

    def test_moderator_invite__invalid_perm(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException) as excinfo:
            subreddit.moderator.invite(self.REDDITOR, permissions=["a"])
        assert excinfo.value.items[0].error_type == "INVALID_PERMISSIONS"

    def test_moderator_invite__no_perms(self, reddit):
        reddit.read_only = False
        # Moderators can only be invited.
        # As of 2016-03-18 there is no API endpoint to get the moderator
        # invite list.
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.invite(self.REDDITOR, permissions=[])
        assert self.REDDITOR not in subreddit.moderator()

    def test_moderator_invited_moderators(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        invited = subreddit.moderator.invited()
        assert isinstance(invited, ListingGenerator)
        for moderator in invited:
            assert isinstance(moderator, Redditor)

    def test_moderator_leave(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.leave()

    def test_moderator_remove_invite(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.remove_invite(self.REDDITOR)

    def test_moderator_update(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.update(self.REDDITOR, permissions=["config"])

    def test_moderator_update_invite(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.moderator.update_invite(self.REDDITOR, permissions=["mail"])

    def test_muted(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        self._add_remove(subreddit, "muted", self.REDDITOR)

    def test_wiki_banned(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        self._add_remove(subreddit.wiki, "banned", self.REDDITOR)

    def test_wiki_contributor(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        self._add_remove(subreddit.wiki, "contributor", self.REDDITOR)


class TestSubredditStreams(IntegrationTest):
    def test_comments(self, reddit):
        subreddit = reddit.subreddit("all")
        generator = subreddit.stream.comments()
        for i in range(400):
            assert isinstance(next(generator), Comment)

    def test_comments__with_pause(self, reddit):
        comment_stream = reddit.subreddit("kakapo").stream.comments(pause_after=0)
        comment_count = 1
        pause_count = 1
        comment = next(comment_stream)
        while comment is not None:
            comment_count += 1
            comment = next(comment_stream)
        while comment is None:
            pause_count += 1
            comment = next(comment_stream)
        assert comment_count == 17
        assert pause_count == 2

    @pytest.mark.cassette_name("TestSubredditStreams.test_comments__with_pause")
    def test_comments__with_skip_existing(self, reddit):
        subreddit = reddit.subreddit("all")
        generator = subreddit.stream.comments(skip_existing=True)
        count = 0
        try:
            for comment in generator:
                count += 1
        except RequestException:
            pass
        # This test uses the same cassette as test_comments which shows
        # that there are at least 400 comments in the stream.
        assert count < 400

    def test_submissions(self, reddit):
        subreddit = reddit.subreddit("all")
        generator = subreddit.stream.submissions()
        for i in range(101):
            assert isinstance(next(generator), Submission)

    @pytest.mark.cassette_name("TestSubredditStreams.test_submissions")
    def test_submissions__with_pause(self, reddit):
        subreddit = reddit.subreddit("all")
        generator = subreddit.stream.submissions(pause_after=-1)
        submission = next(generator)
        submission_count = 0
        while submission is not None:
            submission_count += 1
            submission = next(generator)
        assert submission_count == 100

    @pytest.mark.cassette_name("TestSubredditStreams.test_submissions")
    def test_submissions__with_pause_and_skip_after(self, reddit):
        subreddit = reddit.subreddit("all")
        generator = subreddit.stream.submissions(pause_after=-1, skip_existing=True)
        submission = next(generator)
        assert submission is None  # The first thing yielded should be None
        submission_count = 0
        submission = next(generator)
        while submission is not None:
            submission_count += 1
            submission = next(generator)
        assert submission_count < 100


class TestSubredditStylesheet(IntegrationTest):
    def test_call(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        stylesheet = subreddit.stylesheet()
        assert isinstance(stylesheet, Stylesheet)
        assert len(stylesheet.images) > 0
        assert stylesheet.stylesheet != ""

    def test_delete_banner(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_banner()

    def test_delete_banner_additional_image(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_banner_additional_image()

    def test_delete_banner_hover_image(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_banner_hover_image()

    def test_delete_header(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_header()

    def test_delete_image(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_image("praw")

    def test_delete_mobile_banner(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_mobile_banner()

    def test_delete_mobile_header(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_mobile_header()

    def test_delete_mobile_icon(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.delete_mobile_icon()

    def test_update(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.update("p { color: red; }")

    def test_update__with_reason(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.update("div { color: red; }", reason="use div")

    def test_upload(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.stylesheet.upload(
            name="praw", image_path=image_path("white-square.png")
        )
        assert response["img_src"].endswith(".png")

    def test_upload__invalid(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException) as excinfo:
            subreddit.stylesheet.upload(
                name="praw", image_path=image_path("invalid.jpg")
            )
        assert excinfo.value.items[0].error_type == "IMAGE_ERROR"

    def test_upload__invalid_ext(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException) as excinfo:
            subreddit.stylesheet.upload(
                name="praw.png", image_path=image_path("white-square.png")
            )
        assert excinfo.value.items[0].error_type == "BAD_CSS_NAME"

    def test_upload__others_invalid(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for method in ["upload_header", "upload_mobile_header", "upload_mobile_icon"]:
            with pytest.raises(RedditAPIException) as excinfo:
                getattr(subreddit.stylesheet, method)(image_path("invalid.jpg"))
            assert excinfo.value.items[0].error_type == "IMAGE_ERROR"

    def test_upload__others_too_large(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for method in ["upload_header", "upload_mobile_header", "upload_mobile_icon"]:
            with pytest.raises(TooLarge):
                getattr(subreddit.stylesheet, method)(image_path("too_large.jpg"))

    def test_upload__too_large(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(TooLarge):
            subreddit.stylesheet.upload(
                name="praw", image_path=image_path("too_large.jpg")
            )

    def test_upload_banner__jpg(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_banner(image_path("white-square.jpg"))

    def test_upload_banner__png(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_banner(image_path("white-square.png"))

    def test_upload_banner_additional_image__align(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for alignment in ("left", "centered", "right"):
            subreddit.stylesheet.upload_banner_additional_image(
                image_path("white-square.png"), align=alignment
            )

    def test_upload_banner_additional_image__jpg(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_banner_additional_image(
            image_path("white-square.jpg")
        )

    def test_upload_banner_additional_image__png(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_banner_additional_image(
            image_path("white-square.png")
        )

    def test_upload_banner_hover_image__jpg(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_banner_additional_image(
            image_path("white-square.png")
        )
        subreddit.stylesheet.upload_banner_hover_image(image_path("white-square.jpg"))

    def test_upload_banner_hover_image__png(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_banner_additional_image(
            image_path("white-square.jpg")
        )
        subreddit.stylesheet.upload_banner_hover_image(image_path("white-square.png"))

    def test_upload_header__jpg(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.stylesheet.upload_header(image_path("white-square.jpg"))
        assert response["img_src"].endswith(".jpg")

    def test_upload_header__png(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.stylesheet.upload_header(image_path("white-square.png"))
        assert response["img_src"].endswith(".png")

    def test_upload_mobile_banner__jpg(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_mobile_banner(image_path("white-square.jpg"))

    def test_upload_mobile_banner__png(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.stylesheet.upload_mobile_banner(image_path("white-square.png"))

    def test_upload_mobile_header(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.stylesheet.upload_mobile_header(image_path("header.jpg"))
        assert response["img_src"].endswith(".jpg")

    def test_upload_mobile_icon(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        response = subreddit.stylesheet.upload_mobile_icon(image_path("icon.jpg"))
        assert response["img_src"].endswith(".jpg")


class TestSubredditWiki(IntegrationTest):
    def test__iter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        count = 0
        for wikipage in subreddit.wiki:
            assert isinstance(wikipage, WikiPage)
            count += 1
        assert count > 0

    def test_create(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        wikipage = subreddit.wiki.create(
            name="PRAW New Page", content="This is the new wiki page"
        )
        assert wikipage.name == "praw_new_page"
        assert wikipage.content_md == "This is the new wiki page"

    def test_revisions(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        count = 0
        for revision in subreddit.wiki.revisions(limit=4):
            count += 1
            assert isinstance(revision["author"], Redditor)
            assert isinstance(revision["page"], WikiPage)
        assert count == 4


class WebsocketMock:
    POST_URL = "https://reddit.com/r/<TEST_SUBREDDIT>/comments/{}/test_title/"

    @classmethod
    def make_dict(cls, post_id):
        return {"payload": {"redirect": cls.POST_URL.format(post_id)}}

    def __call__(self, *args, **kwargs):
        return self

    def __init__(self, *post_ids):
        self.post_ids = post_ids
        self.i = -1

    def close(self, *args, **kwargs):
        pass

    def recv(self):
        if not self.post_ids:
            raise websocket.WebSocketTimeoutException()
        assert 0 <= self.i + 1 < len(self.post_ids)
        self.i += 1
        return dumps(self.make_dict(self.post_ids[self.i]))


class WebsocketMockException:
    def __init__(self, close_exc=None, recv_exc=None):
        """Initialize a WebsocketMockException.

        :param recv_exc: An exception to be raised during a call to recv().
        :param close_exc: An exception to be raised during close().

        The purpose of this class is to mock a WebSockets connection that is faulty or
        times out, to see how PRAW handles it.

        """
        self._recv_exc = recv_exc
        self._close_exc = close_exc

    def close(self, *args, **kwargs):
        if self._close_exc is not None:
            raise self._close_exc

    def recv(self):
        if self._recv_exc is not None:
            raise self._recv_exc
        else:
            return dumps(
                {
                    "payload": {
                        "redirect": "https://reddit.com/r/<TEST_SUBREDDIT>/comments/abcdef/test_title/"
                    }
                }
            )


class TestSubreddit(IntegrationTest):
    def test_create(self, reddit):
        reddit.read_only = False
        new_name = "PRAW_rrldkyrfln"
        subreddit = reddit.subreddit.create(
            new_name,
            link_type="any",
            subreddit_type="public",
            title="Sub",
            wikimode="disabled",
            # wiki_edit_age=0,  # these are required now
            # wiki_edit_karma=0,
            # comment_score_hide_mins=0,
        )
        assert subreddit.display_name == new_name
        assert subreddit.submission_type == "any"

    def test_create__exists(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            reddit.subreddit.create(
                "redditdev",
                link_type="any",
                subreddit_type="public",
                title="redditdev",
                wikimode="disabled",
            )
        assert excinfo.value.items[0].error_type == "SUBREDDIT_EXISTS"

    def test_create__invalid_parameter(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            # Supplying invalid setting for link_type
            reddit.subreddit.create(
                "PRAW_iavynavffv",
                link_type="abcd",
                subreddit_type="public",
                title="sub",
                wikimode="disabled",
            )
        assert excinfo.value.items[0].error_type == "INVALID_OPTION"

    def test_create__missing_parameter(self, reddit):
        reddit.read_only = False
        with pytest.raises(RedditAPIException) as excinfo:
            # Not supplying required field title.
            reddit.subreddit.create(
                "PRAW_iavynavffv",
                link_type="any",
                subreddit_type="public",
                title=None,
                wikimode="disabled",
            )
        assert excinfo.value.items[0].error_type == "NO_TEXT"

    def test_message(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.message(subject="Test from PRAW", message="Test content")

    def test_post_requirements(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        data = subreddit.post_requirements()
        tags = [
            "domain_blacklist",
            "body_restriction_policy",
            "domain_whitelist",
            "title_regexes",
            "body_blacklisted_strings",
            "body_required_strings",
            "title_text_min_length",
            "is_flair_required",
            "title_text_max_length",
            "body_regexes",
            "link_repost_age",
            "body_text_min_length",
            "link_restriction_policy",
            "body_text_max_length",
            "title_required_strings",
            "title_blacklisted_strings",
            "guidelines_text",
            "guidelines_display_policy",
        ]
        assert list(data) == tags

    def test_random(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submissions = [
            subreddit.random(),
            subreddit.random(),
            subreddit.random(),
            subreddit.random(),
        ]
        assert len(submissions) == len(set(submissions))

    def test_random__returns_none(self, reddit):
        subreddit = reddit.subreddit("wallpapers")
        assert subreddit.random() is None

    def test_search(self, reddit):
        subreddit = reddit.subreddit("all")
        for item in subreddit.search(
            "praw oauth search", syntax="cloudsearch", limit=None
        ):
            assert isinstance(item, Submission)

    def test_sticky(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.sticky()
        assert isinstance(submission, Submission)

    def test_sticky__not_set(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(NotFound):
            subreddit.sticky(number=2)

    def test_submit__flair(self, reddit):
        flair_id = "17bf09c4-520c-11e7-8073-0ef8adb5ef68"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit(
            "Test Title",
            flair_id=flair_id,
            flair_text=flair_text,
            selftext="Test text.",
        )
        assert submission.link_flair_css_class == flair_class
        assert submission.link_flair_text == flair_text

    def test_submit__nsfw(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit("Test Title", nsfw=True, selftext="Test text.")
        assert submission.over_18 is True

    def test_submit__selftext(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit("Test Title", selftext="Test text.")
        assert submission.author == pytest.placeholders.username
        assert submission.selftext == "Test text."
        assert submission.title == "Test Title"

    def test_submit__selftext_blank(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit("Test Title", selftext="")
        assert submission.author == pytest.placeholders.username
        assert submission.selftext == ""
        assert submission.title == "Test Title"

    def test_submit__selftext_inline_media(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        gif = InlineGif(image_path("test.gif"), "optional caption")
        image = InlineImage(image_path("test.png"), "optional caption")
        video = InlineVideo(image_path("test.mp4"), "optional caption")
        selftext = (
            "Text with a gif {gif1} an image {image1} and a video {video1}" " inline"
        )
        media = {"gif1": gif, "image1": image, "video1": video}
        submission = subreddit.submit("title", inline_media=media, selftext=selftext)
        assert submission.author == pytest.placeholders.username
        assert (
            submission.selftext == "Text with a gif\n\n[optional"
            " caption](https://i.redd.it/3vwgfvq3tyq51.gif)\n\nan"
            " image\n\n[optional"
            " caption](https://preview.redd.it/9147est3tyq51.png?width=128&format=png&auto=webp&s=54d1a865a9339dcca9ec19eb1e357079c81e5100)\n\nand"
            " a video\n\n[optional"
            " caption](https://reddit.com/link/j4p2rk/video/vsie20v3tyq51/player)\n\ninline"
        )
        assert submission.title == "title"

    def test_submit__spoiler(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit("Test Title", selftext="Test text.", spoiler=True)
        assert submission.spoiler is True

    def test_submit__url(self, reddit):
        url = "https://praw.readthedocs.org/en/stable/"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit("Test Title", url=url)
        assert submission.author == pytest.placeholders.username
        assert submission.url == url
        assert submission.title == "Test Title"

    def test_submit__verify_invalid(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        reddit.validate_on_submit = True
        with pytest.raises(
            (RedditAPIException, BadRequest)
        ):  # waiting for prawcore fix
            subreddit.submit("dfgfdgfdgdf", url="https://www.google.com")

    def test_submit_gallery(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        images = [
            {"image_path": image_path("test.png")},
            {"image_path": image_path("test.jpg"), "caption": "test.jpg"},
            {
                "image_path": image_path("test.gif"),
                "outbound_url": "https://example.com",
            },
            {
                "image_path": image_path("test.png"),
                "caption": "test.png",
                "outbound_url": "https://example.com",
            },
        ]

        submission = subreddit.submit_gallery("Test Title", images)
        assert submission.author == pytest.placeholders.username
        assert submission.is_gallery
        assert submission.title == "Test Title"
        items = submission.gallery_data["items"]
        assert isinstance(submission.gallery_data["items"], list)
        for i, item in enumerate(items):
            test_data = images[i]
            test_data.pop("image_path")
            item.pop("id")
            item.pop("media_id")
            assert item == test_data

    def test_submit_gallery__disabled(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        images = [
            {"image_path": image_path("test.png")},
            {"image_path": image_path("test.jpg"), "caption": "test.jpg"},
            {
                "image_path": image_path("test.gif"),
                "outbound_url": "https://example.com",
            },
            {
                "image_path": image_path("test.png"),
                "caption": "test.png",
                "outbound_url": "https://example.com",
            },
        ]

        with pytest.raises(RedditAPIException):
            subreddit.submit_gallery("Test Title", images)

    def test_submit_gallery__flair(self, image_path, reddit):
        flair_id = "6fc213da-cae7-11ea-9274-0e2407099e45"
        flair_text = "test"
        flair_class = "test-flair-class"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        images = [
            {"image_path": image_path("test.png")},
            {"image_path": image_path("test.jpg"), "caption": "test.jpg"},
            {
                "image_path": image_path("test.gif"),
                "outbound_url": "https://example.com",
            },
            {
                "image_path": image_path("test.png"),
                "caption": "test.png",
                "outbound_url": "https://example.com",
            },
        ]
        submission = subreddit.submit_gallery(
            "Test Title", images, flair_id=flair_id, flair_text=flair_text
        )
        assert submission.link_flair_css_class == flair_class
        assert submission.link_flair_text == flair_text

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMock("k5rhpg", "k5rhsu", "k5rhx3")
        ),  # update with cassette
    )
    def test_submit_image(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for i, file_name in enumerate(("test.png", "test.jpg", "test.gif")):
            image = image_path(file_name)
            submission = subreddit.submit_image(f"Test Title {i}", image)
            assert submission.author == pytest.placeholders.username
            assert submission.is_reddit_media_domain
            assert submission.title == f"Test Title {i}"

    @pytest.mark.cassette_name("TestSubreddit.test_submit_image")
    @mock.patch(
        "websocket.create_connection", new=MagicMock(return_value=WebsocketMock())
    )
    def test_submit_image__bad_websocket(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.png", "test.jpg"):
            image = image_path(file_name)
            with pytest.raises(ClientException):
                subreddit.submit_image("Test Title", image)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(return_value=WebsocketMock("ah3gqo")),
    )  # update with cassette
    def test_submit_image__flair(self, image_path, reddit):
        flair_id = "6bd28436-1aa7-11e9-9902-0e05ab0fad46"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        submission = subreddit.submit_image(
            "Test Title", image, flair_id=flair_id, flair_text=flair_text
        )
        assert submission.link_flair_css_class == flair_class
        assert submission.link_flair_text == flair_text

    def test_submit_image__large(self, image_path, reddit, tmp_path):
        reddit.read_only = False

        mock_data = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Error>"
            "<Code>EntityTooLarge</Code>"
            "<Message>Your proposed upload exceeds the maximum allowed size</Message>"
            "<ProposedSize>20971528</ProposedSize>"
            "<MaxSizeAllowed>20971520</MaxSizeAllowed>"
            "<RequestId>23F056D6990D87E0</RequestId>"
            "<HostId>iYEVOuRfbLiKwMgHt2ewqQRIm0NWL79uiC2rPLj9P0PwW55MhjY2/O8d9JdKTf1iwzLjwWMnGQ=</HostId>"
            "</Error>"
        )
        _post = reddit._core._requestor._http.post

        def patch_request(url, *args, **kwargs):
            """Patch requests to return mock data on specific url."""
            if "https://reddit-uploaded-media.s3-accelerate.amazonaws.com" in url:
                response = requests.Response()
                response._content = mock_data.encode("utf-8")
                response.encoding = "utf-8"
                response.status_code = 400
                return response
            return _post(url, *args, **kwargs)

        reddit._core._requestor._http.post = patch_request
        fake_png = PNG_HEADER + b"\x1a" * 10  # Normally 1024 ** 2 * 20 (20 MB)
        with open(tmp_path.joinpath("fake_img.png"), "wb") as tempfile:
            tempfile.write(fake_png)
        subreddit = reddit.subreddit("test")
        with pytest.raises(TooLargeMediaException):
            subreddit.submit_image("test", tempfile.name)
        reddit._core._requestor._http.post = _post

    @mock.patch(
        "websocket.create_connection", new=MagicMock(side_effect=BlockingIOError)
    )  # happens with timeout=0
    def test_submit_image__timeout_1(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        with pytest.raises(WebSocketException):
            subreddit.submit_image("Test Title", image)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            side_effect=socket.timeout
            # happens with timeout=0.00001
        ),
    )
    def test_submit_image__timeout_2(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        with pytest.raises(WebSocketException):
            subreddit.submit_image("Test Title", image)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMockException(
                recv_exc=websocket.WebSocketTimeoutException()
            ),  # happens with timeout=0.1
        ),
    )
    def test_submit_image__timeout_3(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        with pytest.raises(WebSocketException):
            subreddit.submit_image("Test Title", image)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMockException(
                close_exc=websocket.WebSocketTimeoutException()
            ),  # could happen, and PRAW should handle it
        ),
    )
    def test_submit_image__timeout_4(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        with pytest.raises(WebSocketException):
            subreddit.submit_image("Test Title", image)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMockException(
                recv_exc=websocket.WebSocketConnectionClosedException()
            ),  # from issue #1124
        ),
    )
    def test_submit_image__timeout_5(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        with pytest.raises(WebSocketException):
            subreddit.submit_image("Test Title", image)

    def test_submit_image__without_websockets(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.png", "test.jpg", "test.gif"):
            image = image_path(file_name)
            submission = subreddit.submit_image(
                "Test Title", image, without_websockets=True
            )
            assert submission is None

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(return_value=WebsocketMock("k5s3b3")),
    )  # update with cassette
    def test_submit_image_chat(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        submission = subreddit.submit_image("Test Title", image, discussion_type="CHAT")
        assert submission.discussion_type == "CHAT"

    def test_submit_image_verify_invalid(self, image_path, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        image = image_path("test.jpg")
        with pytest.raises(
            (RedditAPIException, BadRequest)
        ):  # waiting for prawcore fix
            subreddit.submit_image(
                "gdfgfdgdgdgfgfdgdfgfdgfdg", image, without_websockets=True
            )

    def test_submit_live_chat(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit("Test Title", discussion_type="CHAT", selftext="")
        assert submission.discussion_type == "CHAT"

    def test_submit_poll(self, reddit):
        options = ["Yes", "No", "3", "4", "5", "6"]
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit_poll(
            "Test Poll", duration=6, options=options, selftext="Test poll text."
        )
        assert submission.author == pytest.placeholders.username
        assert submission.selftext.startswith("Test poll text.")
        assert submission.title == "Test Poll"
        assert [str(option) for option in submission.poll_data.options] == options
        assert submission.poll_data.voting_end_timestamp > submission.created_utc

    def test_submit_poll__flair(self, reddit):
        flair_id = "9ac711a4-1ddf-11e9-aaaa-0e22784c70ce"
        flair_text = "Test flair text"
        flair_class = ""
        options = ["Yes", "No"]
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit_poll(
            "Test Poll",
            duration=6,
            flair_id=flair_id,
            flair_text=flair_text,
            options=options,
            selftext="Test poll text.",
        )
        assert submission.link_flair_text == flair_text
        assert submission.link_flair_css_class == flair_class

    def test_submit_poll__live_chat(self, reddit):
        options = ["Yes", "No"]
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        submission = subreddit.submit_poll(
            "Test Poll",
            discussion_type="CHAT",
            duration=2,
            options=options,
            selftext="",
        )
        assert submission.discussion_type == "CHAT"

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMock("k5rsq3", "k5rt9d"),  # update with cassette
        ),
    )
    def test_submit_video(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for i, file_name in enumerate(("test.mov", "test.mp4")):
            video = image_path(file_name)
            submission = subreddit.submit_video(f"Test Title {i}", video)
            assert submission.author == pytest.placeholders.username
            assert submission.is_video
            assert submission.title == f"Test Title {i}"

    @pytest.mark.cassette_name("TestSubreddit.test_submit_video")
    @mock.patch(
        "websocket.create_connection", new=MagicMock(return_value=WebsocketMock())
    )
    def test_submit_video__bad_websocket(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.mov", "test.mp4"):
            video = image_path(file_name)
            with pytest.raises(ClientException):
                subreddit.submit_video("Test Title", video)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(return_value=WebsocketMock("ahells")),
    )  # update with cassette
    def test_submit_video__flair(self, image_path, reddit):
        flair_id = "6bd28436-1aa7-11e9-9902-0e05ab0fad46"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        submission = subreddit.submit_video(
            "Test Title", video, flair_id=flair_id, flair_text=flair_text
        )
        assert submission.link_flair_css_class == flair_class
        assert submission.link_flair_text == flair_text

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMock("k5rvt5", "k5rwbo")
        ),  # update with cassette
    )
    def test_submit_video__thumbnail(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for video_name, thumb_name in (
            ("test.mov", "test.jpg"),
            ("test.mp4", "test.png"),
        ):
            video = image_path(video_name)
            thumb = image_path(thumb_name)
            submission = subreddit.submit_video(
                "Test Title", video, thumbnail_path=thumb
            )
            assert submission.author == pytest.placeholders.username
            assert submission.is_video
            assert submission.title == "Test Title"

    @mock.patch(
        "websocket.create_connection", new=MagicMock(side_effect=BlockingIOError)
    )  # happens with timeout=0
    def test_submit_video__timeout_1(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        with pytest.raises(WebSocketException):
            subreddit.submit_video("Test Title", video)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            side_effect=socket.timeout
            # happens with timeout=0.00001
        ),
    )
    def test_submit_video__timeout_2(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        with pytest.raises(WebSocketException):
            subreddit.submit_video("Test Title", video)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMockException(
                recv_exc=websocket.WebSocketTimeoutException()
            ),  # happens with timeout=0.1
        ),
    )
    def test_submit_video__timeout_3(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        with pytest.raises(WebSocketException):
            subreddit.submit_video("Test Title", video)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMockException(
                close_exc=websocket.WebSocketTimeoutException()
            ),  # could happen, and PRAW should handle it
        ),
    )
    def test_submit_video__timeout_4(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        with pytest.raises(WebSocketException):
            subreddit.submit_video("Test Title", video)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMockException(
                close_exc=websocket.WebSocketConnectionClosedException()
            ),  # from issue #1124
        ),
    )
    def test_submit_video__timeout_5(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        with pytest.raises(WebSocketException):
            subreddit.submit_video("Test Title", video)

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(
            return_value=WebsocketMock("k5s10u", "k5s11v"),  # update with cassette
        ),
    )
    def test_submit_video__videogif(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.mov", "test.mp4"):
            video = image_path(file_name)
            submission = subreddit.submit_video("Test Title", video, videogif=True)
            assert submission.author == pytest.placeholders.username
            assert submission.is_video
            assert submission.title == "Test Title"

    def test_submit_video__without_websockets(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.mov", "test.mp4"):
            video = image_path(file_name)
            submission = subreddit.submit_video(
                "Test Title", video, without_websockets=True
            )
            assert submission is None

    @mock.patch(
        "websocket.create_connection",
        new=MagicMock(return_value=WebsocketMock("flnyhf")),
    )  # update with cassette
    def test_submit_video_chat(self, image_path, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        submission = subreddit.submit_video("Test Title", video, discussion_type="CHAT")
        assert submission.discussion_type == "CHAT"

    def test_submit_video_verify_invalid(self, image_path, reddit):
        reddit.read_only = False
        reddit.validate_on_submit = True
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        video = image_path("test.mov")
        with pytest.raises(
            (RedditAPIException, BadRequest)
        ):  # waiting for prawcore fix
            subreddit.submit_video(
                "gdfgfdgdgdgfgfdgdfgfdgfdg", video, without_websockets=True
            )

    def test_subscribe(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.subscribe()

    def test_subscribe__multiple(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.subscribe(other_subreddits=["redditdev", reddit.subreddit("iama")])

    def test_traffic(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        traffic = subreddit.traffic()
        assert isinstance(traffic, dict)

    def test_traffic__not_public(self, reddit):
        subreddit = reddit.subreddit("announcements")
        with pytest.raises(NotFound):
            subreddit.traffic()

    def test_unsubscribe(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.unsubscribe()

    def test_unsubscribe__multiple(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.unsubscribe(other_subreddits=["redditdev", reddit.subreddit("iama")])
