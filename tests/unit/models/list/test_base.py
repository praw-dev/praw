"""Test praw.models.list.base."""
import pytest

from praw.models.list.base import BaseList


class TestBaseList(object):
    def setup(self):
        self._prev_child_attribute = BaseList.CHILD_ATTRIBUTE
        self._prev_convert = BaseList._convert

    def teardown(self):
        BaseList.CHILD_ATTRIBUTE = self._prev_child_attribute
        BaseList._convert = staticmethod(self._prev_convert)

    def test__init__CHILD_ATTRIBUTE_not_set(self):
        with pytest.raises(NotImplementedError):
            BaseList(None, None)

    def test__init___convert_not_extended(self):
        BaseList.CHILD_ATTRIBUTE = 'praw'
        with pytest.raises(NotImplementedError):
            BaseList(None, {'praw': [1]})

    def test__contains__(self):
        BaseList._convert = staticmethod(lambda _a, _b: None)
        BaseList.CHILD_ATTRIBUTE = 'praw'
        items = ['foo', 1, {'a': 'b'}]
        base_list = BaseList(None, {'praw': items})
        for item in items:
            assert item in base_list

    def test__getitem__(self):
        BaseList._convert = staticmethod(lambda _a, _b: None)
        BaseList.CHILD_ATTRIBUTE = 'praw'
        items = ['foo', 1, {'a': 'b'}]
        base_list = BaseList(None, {'praw': items})
        for i, item in enumerate(items):
            assert item == base_list[i]

    def test__iter__(self):
        BaseList._convert = staticmethod(lambda _a, _b: None)
        BaseList.CHILD_ATTRIBUTE = 'praw'
        items = ['foo', 1, {'a': 'b'}]
        base_list = BaseList(None, {'praw': items})
        for i, item in enumerate(base_list):
            assert items[i] == item

    def test__str__(self):
        BaseList._convert = staticmethod(lambda _a, _b: None)
        BaseList.CHILD_ATTRIBUTE = 'praw'
        items = ['foo', 1, {'a': 'b'}]
        base_list = BaseList(None, {'praw': items})
        assert str(items) == str(base_list)
