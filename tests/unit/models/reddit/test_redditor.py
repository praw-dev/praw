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
            Redditor(reddit, name="dummy", fullname="t2_dummy")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Redditor(
                reddit,
                name="dummy",
                fullname="t2_dummy",
                _data={"id": "dummy"},
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
        redditor1 = Redditor(reddit, _data={"name": "dummy1", "n": 1})
        redditor2 = Redditor(reddit, _data={"name": "Dummy1", "n": 2})
        redditor3 = Redditor(reddit, _data={"name": "dummy3", "n": 2})
        assert redditor1 == redditor1
        assert redditor2 == redditor2
        assert redditor3 == redditor3
        assert redditor1 == redditor2
        assert redditor2 != redditor3
        assert redditor1 != redditor3
        assert "dummy1" == redditor1
        assert redditor2 == "dummy1"

    def test_fullname(self, reddit):
        redditor = Redditor(reddit, _data={"name": "name", "id": "dummy"})
        assert redditor.fullname == "t2_dummy"

    def test_guild__max(self, reddit):
        with pytest.raises(TypeError) as excinfo:
            Redditor(reddit, name="RedditorName").gild(months=37)
        assert str(excinfo.value) == "months must be between 1 and 36"

    def test_guild__min(self, reddit):
        with pytest.raises(TypeError) as excinfo:
            Redditor(reddit, name="RedditorName").gild(months=0)
        assert str(excinfo.value) == "months must be between 1 and 36"

    def test_hash(self, reddit):
        redditor1 = Redditor(reddit, _data={"name": "dummy1", "n": 1})
        redditor2 = Redditor(reddit, _data={"name": "Dummy1", "n": 2})
        redditor3 = Redditor(reddit, _data={"name": "dummy3", "n": 2})
        assert hash(redditor1) == hash(redditor1)
        assert hash(redditor2) == hash(redditor2)
        assert hash(redditor3) == hash(redditor3)
        assert hash(redditor1) == hash(redditor2)
        assert hash(redditor2) != hash(redditor3)
        assert hash(redditor1) != hash(redditor3)

    def test_pickle(self, reddit):
        redditor = Redditor(reddit, _data={"name": "name", "id": "dummy"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(redditor, protocol=level))
            assert redditor == other

    def test_repr(self, reddit):
        redditor = Redditor(reddit, name="RedditorName")
        assert repr(redditor) == "Redditor(name='RedditorName')"

    def test_str(self, reddit):
        redditor = Redditor(reddit, _data={"name": "name", "id": "dummy"})
        assert str(redditor) == "name"


class TestRedditorListings(UnitTest):
    def test__params_not_modified_in_mixed_listing(self, reddit):
        params = {"dummy": "value"}
        redditor = Redditor(reddit, name="spez")
        for listing in ["controversial", "hot", "new", "top"]:
            generator = getattr(redditor, listing)(params=params)
            assert params == {"dummy": "value"}
            assert listing == generator.params["sort"]
            assert "value" == generator.params["dummy"]
