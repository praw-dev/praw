import pytest
from praw.models import Submission

from .. import UnitTest


class TestSubmission(UnitTest):
    def test_id_from_url(self):
        urls = ['http://my.it/2gmzqe',
                'https://redd.it/2gmzqe',
                'http://reddit.com/comments/2gmzqe',
                'https://www.reddit.com/r/redditdev/comments/2gmzqe/'
                'praw_https_enabled_praw_testing_needed/']
        for url in urls:
            assert Submission.id_from_url(url) == '2gmzqe', url

    def test_id_from_url__invalid_urls(self):
        urls = ['', '1', '/', 'my.it/2gmzqe',
                'http://my.it/_',
                'https://redd.it/_/',
                'http://reddit.com/comments/_/2gmzqe']
        for url in urls:
            with pytest.raises(AttributeError):
                print(Submission.id_from_url(url))
