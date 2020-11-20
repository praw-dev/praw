import pickle

import pytest

from praw.exceptions import ClientException
from praw.models import Comment

from ... import UnitTest


class TestComment(UnitTest):
    def test_attribute_error(self):
        with pytest.raises(AttributeError):
            Comment(self.reddit, _data={"id": "1"}).mark_as_read()

    def test_equality(self):
        comment1 = Comment(self.reddit, _data={"id": "dummy1", "n": 1})
        comment2 = Comment(self.reddit, _data={"id": "Dummy1", "n": 2})
        comment3 = Comment(self.reddit, _data={"id": "dummy3", "n": 2})
        assert comment1 == comment1
        assert comment2 == comment2
        assert comment3 == comment3
        assert comment1 == comment2
        assert comment2 != comment3
        assert comment1 != comment3
        assert "dummy1" == comment1
        assert comment2 == "dummy1"

    def test_construct_failure(self):
        message = "Exactly one of `id`, `url`, or `_data` must be provided."
        with pytest.raises(TypeError) as excinfo:
            Comment(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Comment(self.reddit, id="dummy", url="dummy")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Comment(self.reddit, "dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Comment(self.reddit, url="dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Comment(self.reddit, "dummy", "dummy", {"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(ValueError):
            Comment(self.reddit, "")
        with pytest.raises(ValueError):
            Comment(self.reddit, url="")

    def test_construct_from_url(self):
        url = "https://reddit.com/comments/2gmzqe/_/cklhv0f/"
        assert Comment(self.reddit, url=url) == "cklhv0f"

    def test_hash(self):
        comment1 = Comment(self.reddit, _data={"id": "dummy1", "n": 1})
        comment2 = Comment(self.reddit, _data={"id": "Dummy1", "n": 2})
        comment3 = Comment(self.reddit, _data={"id": "dummy3", "n": 2})
        assert hash(comment1) == hash(comment1)
        assert hash(comment2) == hash(comment2)
        assert hash(comment3) == hash(comment3)
        assert hash(comment1) == hash(comment2)
        assert hash(comment2) != hash(comment3)
        assert hash(comment1) != hash(comment3)

    def test_id_from_url(self):
        urls = [
            "http://reddit.com/comments/2gmzqe/_/cklhv0f/",
            "https://reddit.com/comments/2gmzqe/_/cklhv0f",
            "http://www.reddit.com/r/redditdev/comments/2gmzqe/_/cklhv0f/",
            "https://www.reddit.com/r/redditdev/comments/2gmzqe/_/cklhv0f",
        ]
        for url in urls:
            assert Comment.id_from_url(url) == "cklhv0f", url

    def test_id_from_url__invalid_urls(self):
        urls = [
            "",
            "1",
            "/",
            "my.it/2gmzqe",
            "http://my.it/_",
            "https://redd.it/_/",
            "http://reddit.com/comments/_/2gmzqe",
            "http://my.it/2gmzqe",
            "https://redd.it/2gmzqe",
            "http://reddit.com/comments/2gmzqe",
            "https://www.reddit.com/r/redditdev/comments/2gmzqe/",
        ]
        for url in urls:
            with pytest.raises(ClientException):
                Comment.id_from_url(url)

    def test_pickle(self):
        comment = Comment(self.reddit, _data={"id": "dummy"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(comment, protocol=level))
            assert comment == other

    def test_repr(self):
        comment = Comment(self.reddit, id="dummy")
        assert repr(comment) == "Comment(id='dummy')"

    def test_str(self):
        comment = Comment(self.reddit, _data={"id": "dummy"})
        assert str(comment) == "dummy"

    def test_unset_hidden_attribute_does_not_fetch(self):
        comment = Comment(self.reddit, _data={"id": "dummy"})
        assert comment._fetched
        with pytest.raises(AttributeError):
            comment._ipython_canary_method_should_not_exist_
