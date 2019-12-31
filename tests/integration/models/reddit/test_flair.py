"""Test praw.models.reddit.flair"""
import mock
import pytest

from praw.models.reddit.flair import AdvancedSubmissionFlair, RedditorFlair
from ... import IntegrationTest


class TestFlair(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_get_compatible_flairs(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestFlair.test_get_AdvancedSubmissionFlair"
        ):
            submission = self.reddit.submission("ehswem")
            choices = submission.flair.choices(use_flair_class=True)
            for choice in choices:
                advanced = choice.find_advanced_flair_template()
                assert advanced.id == choice.flair_template_id

    @mock.patch("time.sleep", return_value=None)
    def test_invalid_id(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestFlair.test_get_AdvancedSubmissionFlair_invalid"
        ):
            submission = self.reddit.submission("eh0qey")
            choices = submission.flair.choices(use_flair_class=True)
            choice = next(iter(choices))
            choice.flair_template_id = "asdf"
            advanced = choice.find_advanced_flair_template()
            assert advanced is None

    @mock.patch("time.sleep", return_value=None)
    def test_ASF_invalid_id(self, _):
        self.reddit.read_only = False
        missing_id = {
            "type": "text",
            "text_editable": True,
            "allowable_content": "all",
            "text": "Testingint",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Testing",
            "richtext": [],
            "background_color": "#dadada",
        }
        with self.recorder.use_cassette(
            "TestFlair.fetch_AdvancedSubmissionFlair_no_id"
        ):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = AdvancedSubmissionFlair(self.reddit, subreddit, missing_id)
            flair._fetch()
            assert flair._fetched
            print(flair.__dict__)
            assert hasattr(flair, "id")
            assert flair.id == "bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7"

    @mock.patch("time.sleep", return_value=None)
    def test_RF_invalid_id(self, _):
        self.reddit.read_only = False
        missing_id = {
            "allowable_content": "all",
            "text": "sd",
            "text_color": "dark",
            "mod_only": False,
            "background_color": "transparent",
            "css_class": "",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": False,
            "override_css": False,
            "type": "text",
        }
        with self.recorder.use_cassette("TestFlair.fetch_RedditorFlair_no_id"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = RedditorFlair(self.reddit, subreddit, missing_id)
            flair._fetch()
            assert flair._fetched
            print(flair.__dict__)
            assert hasattr(flair, "id")
            assert flair.id == "c6770634-2c0b-11ea-b2c4-0eb2086522d7"

    @mock.patch("time.sleep", return_value=None)
    def test_ASF_only_id(self, _):
        self.reddit.read_only = False
        valid_id = {"id": "bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7"}
        other_details = {
            "type": "text",
            "text_editable": True,
            "allowable_content": "all",
            "text": "Testingint",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Testing",
            "richtext": [],
            "background_color": "#dadada",
        }
        with self.recorder.use_cassette(
            "TestFlair.fetch_AdvancedSubmissionFlair_only_id"
        ):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = AdvancedSubmissionFlair(self.reddit, subreddit, valid_id)
            flair._fetch()
            assert flair._fetched
            print(flair.__dict__)
            for key in other_details.keys():
                assert hasattr(flair, key)
                assert getattr(flair, key) == other_details[key]

    @mock.patch("time.sleep", return_value=None)
    def test_RF_only_id(self, _):
        self.reddit.read_only = False
        valid_id = {"id": "c6770634-2c0b-11ea-b2c4-0eb2086522d7"}
        other_details = {
            "allowable_content": "all",
            "text": "sd",
            "text_color": "dark",
            "mod_only": False,
            "background_color": "transparent",
            "css_class": "",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": False,
            "override_css": False,
            "type": "text",
        }
        with self.recorder.use_cassette(
            "TestFlair.fetch_RedditorFlair_only_id"
        ):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = RedditorFlair(self.reddit, subreddit, valid_id)
            flair._fetch()
            print(flair.__dict__)
            assert flair._fetched
            for key in other_details.keys():
                assert hasattr(flair, key)
                assert getattr(flair, key) == other_details[key]
