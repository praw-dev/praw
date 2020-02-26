"""Test praw.models.reddit.flair"""
import mock
import pytest

from praw.models.reddit.flair import AdvancedSubmissionFlair, RedditorFlair
from praw.exceptions import InvalidFlairTemplateID
from ... import IntegrationTest


class TestFlair(IntegrationTest):
    def _delete_flair(self, flair):
        if isinstance(flair, AdvancedSubmissionFlair):
            sub = flair.subreddit
            sub.flair.link_templates.delete(flair=flair)
        if isinstance(flair, RedditorFlair):
            sub = flair.subreddit
            sub.flair.templates.delete(flair=flair)

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
        invalid_id = {"id": "notexist"}
        with self.recorder.use_cassette("TestFlair.test_ASF_invalid_id"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = AdvancedSubmissionFlair(
                self.reddit, subreddit, _data=invalid_id
            )
            with pytest.raises(InvalidFlairTemplateID):
                flair._fetch()

    @mock.patch("time.sleep", return_value=None)
    def test_RF_invalid_id(self, _):
        self.reddit.read_only = False
        invalid_id = {"id": "notexist"}
        with self.recorder.use_cassette("TestFlair.test_RF_invalid_id"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = RedditorFlair(self.reddit, subreddit, _data=invalid_id)
            with pytest.raises(InvalidFlairTemplateID):
                flair._fetch()

    @mock.patch("time.sleep", return_value=None)
    def test_ASF_only_id(self, _):
        self.reddit.read_only = False
        valid_id = {"id": "bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7"}
        other_details = {
            "type": "richtext",
            "text_editable": True,
            "allowable_content": "all",
            "text": "Testingint",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Testing",
            "richtext": [{"e": "text", "t": "Testingint"}],
            "background_color": "#dadada",
        }
        with self.recorder.use_cassette(
            "TestFlair.fetch_AdvancedSubmissionFlair_only_id"
        ):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair = AdvancedSubmissionFlair(
                self.reddit, subreddit, _data=valid_id
            )
            flair._fetch()
            assert flair._fetched
            print(flair.__dict__)
            for key in other_details.keys():
                assert hasattr(flair, key)
                print(flair, key)
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
            flair = RedditorFlair(self.reddit, subreddit, _data=valid_id)
            flair._fetch()
            print(flair.__dict__)
            assert flair._fetched
            for key in other_details.keys():
                assert hasattr(flair, key)
                assert getattr(flair, key) == other_details[key]

    @mock.patch("time.sleep", return_value=None)
    def test_auto_creation_ASF(self, _):
        self.reddit.read_only = False
        arbritary_number = 124
        with self.recorder.use_cassette("TestFlair.auto_create_submission"):
            submission = self.reddit.submission("eh0qey")
            subreddit = submission.subreddit
            flair = subreddit.flair.link_templates.make(
                "test{num}".format(num=arbritary_number),
                create_before_usage=True,
            )
            submission.flair.select(flair=flair)
            _submission = self.reddit.submission("eh0qey")
            assert _submission.link_flair_text == "test{num}".format(
                num=arbritary_number
            )
            assert "id" in flair.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_auto_creation_RF(self, _):
        self.reddit.read_only = False
        arbritary_number = 124
        with self.recorder.use_cassette("TestFlair.auto_create_redditor"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            user = self.reddit.redditor("spez")
            flair = subreddit.flair.templates.make(
                "test{num}".format(num=arbritary_number),
                create_before_usage=True,
            )
            subreddit.flair.set(user, flair=flair)
            new_entry = [
                data for data in subreddit.flair() if data["user"] == user
            ][0]
            assert new_entry["flair_text"] == "test{num}".format(
                num=arbritary_number
            )

    @mock.patch("time.sleep", return_value=None)
    def test_id_attr_RF_full(self, _):
        self.reddit.read_only = False
        data = {
            "allowable_content": "all",
            "text": "Test",
            "text_color": "light",
            "mod_only": False,
            "background_color": "#cc8b00",
            "id": "0be1ace4-2a75-11ea-8018-0ecef10bc461",
            "css_class": "sdgdsgdfg",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": True,
            "override_css": False,
            "type": "text",
        }
        with self.recorder.use_cassette("TestFlair.check_id_full_RF"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair1 = RedditorFlair(self.reddit, subreddit, _data=data)
            flair1._fetch()
            assert flair1._fetched
            flair2 = RedditorFlair(
                self.reddit,
                subreddit,
                id="0be1ace4-2a75-11ea-8018-0ecef10bc461",
            )
            flair2._fetch()
            assert flair2._fetched
            assert flair1 == flair2
            assert flair1.id == flair2.id
            assert flair1.__dict__ == flair2.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_id_attr_RF_id_only(self, _):
        self.reddit.read_only = False
        data = {"id": "0be1ace4-2a75-11ea-8018-0ecef10bc461"}
        with self.recorder.use_cassette("TestFlair.check_id_only_RF"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair1 = RedditorFlair(self.reddit, subreddit, _data=data)
            flair1._fetch()
            assert flair1._fetched
            flair2 = RedditorFlair(
                self.reddit,
                subreddit,
                id="0be1ace4-2a75-11ea-8018-0ecef10bc461",
            )
            flair2._fetch()
            assert flair2._fetched
            assert flair1 == flair2
            assert flair1.id == flair2.id
            assert flair1.__dict__ == flair2.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_id_attr_RF_id_only_both(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestFlair.check_id_all_RF"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair1 = RedditorFlair(
                self.reddit,
                subreddit,
                id="0be1ace4-2a75-11ea-8018-0ecef10bc461",
            )
            flair1._fetch()
            assert flair1._fetched
            flair2 = RedditorFlair(
                self.reddit,
                subreddit,
                id="0be1ace4-2a75-11ea-8018-0ecef10bc461",
            )
            flair2._fetch()
            assert flair2._fetched
            assert flair1 == flair2
            assert flair1.id == flair2.id
            assert flair1.__dict__ == flair2.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_id_attr_ASF_full(self, _):
        self.reddit.read_only = False
        data = {
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
            "id": "bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7",
        }
        with self.recorder.use_cassette("TestFlair.check_id_full_ASF"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair1 = AdvancedSubmissionFlair(
                self.reddit, subreddit, _data=data
            )
            flair1._fetch()
            assert flair1._fetched
            flair2 = AdvancedSubmissionFlair(
                self.reddit,
                subreddit,
                id="bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7",
            )
            flair2._fetch()
            assert flair2._fetched
            assert flair1 == flair2
            assert flair1.id == flair2.id
            assert flair1.__dict__ == flair2.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_id_attr_ASF_id_only(self, _):
        self.reddit.read_only = False
        data = {"id": "bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7"}
        with self.recorder.use_cassette("TestFlair.check_id_only_ASF"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair1 = AdvancedSubmissionFlair(
                self.reddit, subreddit, _data=data
            )
            flair1._fetch()
            assert flair1._fetched
            flair2 = AdvancedSubmissionFlair(
                self.reddit,
                subreddit,
                id="bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7",
            )
            flair2._fetch()
            assert flair2._fetched
            assert flair1 == flair2
            assert flair1.id == flair2.id
            assert flair1.__dict__ == flair2.__dict__

    @mock.patch("time.sleep", return_value=None)
    def test_id_attr_ASF_id_only_both(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestFlair.check_id_all_ASF"):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            flair1 = AdvancedSubmissionFlair(
                self.reddit,
                subreddit,
                id="bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7",
            )
            flair1._fetch()
            assert flair1._fetched
            flair2 = AdvancedSubmissionFlair(
                self.reddit,
                subreddit,
                id="bfe7bf6e-2a6e-11ea-9d64-0e73c60478f7",
            )
            flair2._fetch()
            assert flair2._fetched
            assert flair1 == flair2
            assert flair1.id == flair2.id
            assert flair1.__dict__ == flair2.__dict__
