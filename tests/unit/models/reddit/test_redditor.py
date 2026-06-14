import pickle

import pytest

from praw.models import Redditor

from ... import UnitTest


class TestRedditor(UnitTest):
    def test_construct_failure(self, reddit):
        message = "Exactly one of 'name', 'fullname', or '_data' must be provided."
        with pytest.raises(TypeError) as excinfo:
            Redditor(reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Redditor(reddit, "dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Redditor(reddit, fullname="t2_dummy", name="dummy")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Redditor(
                reddit,
                _data={"id": "dummy"},
                fullname="t2_dummy",
                name="dummy",
            )
        assert str(excinfo.value) == message

        with pytest.raises(AssertionError):
            Redditor(reddit, _data=[{"name": "dummy"}])

        with pytest.raises(AssertionError):
            Redditor(reddit, _data={"notname": "dummy"})

        with pytest.raises(ValueError):
            Redditor(reddit, "")
        with pytest.raises(ValueError):
            Redditor(reddit, fullname="")

    def test_equality(self, reddit):
        redditor1 = Redditor(reddit, _data={"n": 1, "name": "dummy1"})
        redditor2 = Redditor(reddit, _data={"n": 2, "name": "Dummy1"})
        redditor3 = Redditor(reddit, _data={"n": 2, "name": "dummy3"})
        assert redditor1 == redditor1
        assert redditor2 == redditor2
        assert redditor3 == redditor3
        assert redditor1 == redditor2
        assert redditor2 != redditor3
        assert redditor1 != redditor3
        assert redditor1 == "dummy1"
        assert redditor2 == "dummy1"

    def test_fullname(self, reddit):
        redditor = Redditor(reddit, _data={"id": "dummy", "name": "name"})
        assert redditor.fullname == "t2_dummy"

    def test_hash(self, reddit):
        redditor1 = Redditor(reddit, _data={"n": 1, "name": "dummy1"})
        redditor2 = Redditor(reddit, _data={"n": 2, "name": "Dummy1"})
        redditor3 = Redditor(reddit, _data={"n": 2, "name": "dummy3"})
        assert hash(redditor1) == hash(redditor1)
        assert hash(redditor2) == hash(redditor2)
        assert hash(redditor3) == hash(redditor3)
        assert hash(redditor1) == hash(redditor2)
        assert hash(redditor2) != hash(redditor3)
        assert hash(redditor1) != hash(redditor3)

    def test_pickle(self, reddit):
        redditor = Redditor(reddit, _data={"id": "dummy", "name": "name"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(redditor, protocol=level))
            assert redditor == other

    def test_repr(self, reddit):
        redditor = Redditor(reddit, name="RedditorName")
        assert repr(redditor) == "Redditor(name='RedditorName')"

    def test_str(self, reddit):
        redditor = Redditor(reddit, _data={"id": "dummy", "name": "name"})
        assert str(redditor) == "name"


class TestRedditorListings(UnitTest):
    def test__params_not_modified_in_mixed_listing(self, reddit):
        params = {"dummy": "value"}
        redditor = Redditor(reddit, name="spez")
        for listing in ["controversial", "hot", "new", "top"]:
            generator = getattr(redditor, listing)(params=params)
            assert params == {"dummy": "value"}
            assert listing == generator.params["sort"]
            assert generator.params["dummy"] == "value"

    def test_overview(self, reddit):
        redditor = Redditor(reddit, name="spez")
        assert redditor.overview._path == "user/spez/overview"
