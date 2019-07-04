"""Test praw.models.list.base."""
import pytest

from praw.models.list.base import BaseList


class DummyObjector:
    @staticmethod
    def objectify(value):
        return value


class Dummy:
    def __init__(self):
        self._objector = DummyObjector


class TestBaseList:
    def setup(self):
        self._prev_child_attribute = BaseList.CHILD_ATTRIBUTE

    def teardown(self):
        BaseList.CHILD_ATTRIBUTE = self._prev_child_attribute

    def test__init__CHILD_ATTRIBUTE_not_set(self):
        with pytest.raises(NotImplementedError):
            BaseList(None, None)

    def test__contains__(self):
        BaseList.CHILD_ATTRIBUTE = "praw"
        items = ["foo", 1, {"a": "b"}]
        base_list = BaseList(Dummy(), {"praw": items})
        for item in items:
            assert item in base_list

    def test__getitem__(self):
        BaseList.CHILD_ATTRIBUTE = "praw"
        items = ["foo", 1, {"a": "b"}]
        base_list = BaseList(Dummy(), {"praw": items})
        for i, item in enumerate(items):
            assert item == base_list[i]

    def test__iter__(self):
        BaseList.CHILD_ATTRIBUTE = "praw"
        items = ["foo", 1, {"a": "b"}]
        base_list = BaseList(Dummy(), {"praw": items})
        for i, item in enumerate(base_list):
            assert items[i] == item

    def test__str__(self):
        BaseList.CHILD_ATTRIBUTE = "praw"
        items = ["foo", 1, {"a": "b"}]
        base_list = BaseList(Dummy(), {"praw": items})
        assert str(items) == str(base_list)
