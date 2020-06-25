from praw.models import MoreComments

from ... import IntegrationTest


class TestMore(IntegrationTest):
    def setup(self):
        super().setup()
        # Responses do not decode well on travis so manually renable gzip.
        self.reddit._core._requestor._http.headers["Accept-Encoding"] = "gzip"

    def test_comments(self):
        data = {
            "count": 9,
            "name": "t1_cu5tt8h",
            "id": "cu5tt8h",
            "parent_id": "t3_3hahrw",
            "children": [
                "cu5tt8h",
                "cu5v9yd",
                "cu5twf5",
                "cu5tkk4",
                "cu5tead",
                "cu5rxpy",
                "cu5oufs",
                "cu5tpek",
                "cu5pbdh",
            ],
        }
        with self.use_cassette(match_requests_on=["uri", "method", "body"]):
            more = MoreComments(self.reddit, data)
            more.submission = self.reddit.submission("3hahrw")
            assert len(more.comments()) == 7

    def test_comments__continue_thread_type(self):
        data = {
            "count": 0,
            "name": "t1__",
            "id": "_",
            "parent_id": "t1_cu5v5h7",
            "children": [],
        }
        with self.use_cassette(match_requests_on=["uri", "method", "body"]):
            more = MoreComments(self.reddit, data)
            more.submission = self.reddit.submission("3hahrw")
            assert len(more.comments()) == 1
