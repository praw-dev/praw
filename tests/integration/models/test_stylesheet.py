"""Test praw.models.Stylesheet"""
import mock

from .. import IntegrationTest


class TestStylesheet(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_equality(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestStylesheet.test_equality"):
            subreddit1 = self.reddit.subreddit("test")
            subreddit2 = self.reddit.subreddit("test")
            subreddit3 = self.reddit.user.me().moderated()[0]
            assert subreddit1.stylesheet() == subreddit2.stylesheet()
            assert subreddit1.stylesheet() != subreddit3.stylesheet()
