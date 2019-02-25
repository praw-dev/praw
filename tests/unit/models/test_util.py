"""Test praw.models.util module."""
from collections.abc import MutableMapping
import pickle
import pytest
from .. import UnitTest
from praw.models.util import (
    ExponentialCounter,
    permissions_string,
    AttributeDict
)


class TestExponentialCounter(UnitTest):
    MAX_DELTA = 1. / 32

    def test_exponential_counter__counter(self):
        def assert_range(number, exponent):
            assert number >= 2 ** exponent * (1 - self.MAX_DELTA)
            assert number <= 2 ** exponent * (1 + self.MAX_DELTA)

        counter = ExponentialCounter(1024)
        prev_value = counter.counter()
        assert_range(prev_value, 0)

        for i in range(9):
            value = counter.counter()
            assert_range(value, 1 + i)
            assert value > prev_value
            prev_value = value

    def test_exponential_counter__max_value(self):
        counter = ExponentialCounter(5)
        max_value = 5 * (1 + self.MAX_DELTA)
        for _ in range(100):
            value = counter.counter()
            assert value <= max_value

    def test_exponential_counter__reset(self):
        counter = ExponentialCounter(1024)
        for _ in range(100):
            value = counter.counter()
            assert value >= 1 - self.MAX_DELTA
            assert value <= 1 + self.MAX_DELTA
            counter.reset()


class TestUtil(UnitTest):
    PERMISSIONS = {'a', 'b', 'c'}

    def test_permissions_string__all_explicit(self):
        assert '-all,+b,+a,+c' == permissions_string(['b', 'a', 'c'],
                                                     self.PERMISSIONS)

    def test_permissions_string__empty_list(self):
        assert '-all' == permissions_string([], set())
        assert '-all,-a,-b,-c' == permissions_string([], self.PERMISSIONS)

    def test_permissions_string__none(self):
        assert '+all' == permissions_string(None, set())
        assert '+all' == permissions_string(None, self.PERMISSIONS)

    def test_permissions_string__with_additional_permissions(self):
        assert '-all,+d' == permissions_string(['d'], set())
        assert '-all,-a,-b,-c,+d' == permissions_string(['d'],
                                                        self.PERMISSIONS)


class TestAttributeDict:
    def setup_method(self):
        self.attrdict = AttributeDict({'a': 1, 'b': 2, 'c': 3})
        self.attrdict_dict_nest = AttributeDict({'a': {'b': 3}})

    def test_init(self):
        attrdict1 = AttributeDict()
        attrdict2 = AttributeDict()
        attrdict3 = attrdict4 = AttributeDict()
        assert isinstance(attrdict1, MutableMapping)

        attrdict1['a'] = 10
        assert 'a' in attrdict1
        assert 'a' not in attrdict2
        assert abs(attrdict1) is not abs(attrdict2)

        attrdict3['b'] = 20
        assert 'b' in attrdict3
        assert 'b' in attrdict4
        assert abs(attrdict3) is abs(attrdict4)

        mydict = {'key': 'value'}
        attrdict5 = AttributeDict(mydict, another_key='another_value')
        assert abs(attrdict5) is not mydict
        attrdict5.clear()
        assert mydict == {'key': 'value'}

    def test_getitem(self):
        assert self.attrdict['a'] == 1

        with pytest.raises(KeyError):
            self.attrdict['z']

        assert type(self.attrdict_dict_nest['a']) is dict

    def test_getattr(self):
        assert self.attrdict.a == 1

        with pytest.raises(AttributeError):
            self.attrdict.z

        assert type(self.attrdict_dict_nest.a) is AttributeDict

    def test_setitem(self):
        assert len(self.attrdict) == 3
        self.attrdict['d'] = 4
        assert 'd' in self.attrdict
        assert len(self.attrdict) == 4

    def test_delitem(self):
        assert len(self.attrdict) == 3
        del self.attrdict['a']
        assert 'a' not in self.attrdict
        assert len(self.attrdict) == 2

    def test_iter(self):
        expected_items = {'a', 'b', 'c'}
        found_items = set()
        for item in self.attrdict:
            found_items.add(item)

        assert found_items == expected_items

    def test_str(self):
        assert str(self.attrdict) == "{'a': 1, 'b': 2, 'c': 3}"
        self.attrdict.pop('c')
        assert str(self.attrdict) == "{'a': 1, 'b': 2}"

    def test_repr(self):
        assert repr(self.attrdict) == "AttributeDict({'a': 1, 'b': 2, 'c': 3})"
        self.attrdict.pop('c')
        assert repr(self.attrdict) == "AttributeDict({'a': 1, 'b': 2})"

        attrdict1 = AttributeDict()
        attrdict2 = AttributeDict({})
        assert repr(attrdict1) == repr(attrdict2) == 'AttributeDict()'
        assert abs(attrdict1) is not abs(attrdict2)

        attrdict3 = AttributeDict({'a': 1})
        assert repr(attrdict3) == "AttributeDict({'a': 1})"
        attrdict3.pop('a')
        assert repr(attrdict3) == 'AttributeDict()'

    def test_abs(self):
        mydict = {'key': 'value'}
        attrdict = AttributeDict(mydict)
        mydict['key2'] = 'value2'
        assert 'key2' in attrdict
        assert attrdict['key2'] == 'value2'
        assert abs(attrdict) is mydict

    def test_update(self):
        assert len(self.attrdict) == 3
        self.attrdict.update({'c': 8, 'd': 11})
        assert len(self.attrdict) == 4
        assert self.attrdict['a'] == 1
        assert self.attrdict['b'] == 2
        assert self.attrdict['c'] == 8
        assert self.attrdict['d'] == 11

    def test_clear(self):
        assert len(self.attrdict) == 3
        self.attrdict.clear()
        assert len(self.attrdict) == 0
        assert 'a' not in self.attrdict

    def test_pickle(self):
        mydict = {
            'a': 1,
            'b': 2,
            'c': {
                'dee': 40,
                'eee': {
                    'eff': 'gee',
                    'hch': 80
                }
            },
            'foo': [1, 2, 3]
        }
        attrdict = AttributeDict(mydict)
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(attrdict, protocol=level))
            assert attrdict == other
