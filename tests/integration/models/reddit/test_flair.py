"""Test praw.models.reddit.flair"""
import mock

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
