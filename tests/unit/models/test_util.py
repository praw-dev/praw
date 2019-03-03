"""Test praw.models.util module."""
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
import pickle

import pytest

from .. import UnitTest
from praw.models.util import (
    ExponentialCounter,
    permissions_string,
    AttributeDict,
    AttributeContainer,
    RedditAttributes
)


class TestExponentialCounter(UnitTest):
    MAX_DELTA = 1.0 / 32

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
    PERMISSIONS = {"a", "b", "c"}

    def test_permissions_string__all_explicit(self):
        assert "-all,+b,+a,+c" == permissions_string(
            ["b", "a", "c"], self.PERMISSIONS
        )

    def test_permissions_string__empty_list(self):
        assert "-all" == permissions_string([], set())
        assert "-all,-a,-b,-c" == permissions_string([], self.PERMISSIONS)

    def test_permissions_string__none(self):
        assert "+all" == permissions_string(None, set())
        assert "+all" == permissions_string(None, self.PERMISSIONS)

    def test_permissions_string__with_additional_permissions(self):
        assert '-all,+d' == permissions_string(['d'], set())
        assert '-all,-a,-b,-c,+d' == permissions_string(['d'],
                                                        self.PERMISSIONS)


class TestAttributeDict(UnitTest):
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

    def test_getattr(self):
        assert self.attrdict.a == 1

        with pytest.raises(AttributeError):
            self.attrdict.z

        assert type(self.attrdict_dict_nest.a) is AttributeDict

    def test_setattr(self):
        assert len(self.attrdict) == 3
        self.attrdict.d = 4
        assert 'd' in self.attrdict
        assert len(self.attrdict) == 4

    def test_delattr(self):
        assert len(self.attrdict) == 3
        del self.attrdict.a
        assert 'a' not in self.attrdict
        assert len(self.attrdict) == 2

    def test_iter(self):
        expected_items = {'a', 'b', 'c'}
        found_items = set()
        for item in self.attrdict:
            found_items.add(item)

        assert found_items == expected_items

    def test_str(self):
        def assert_attrdict_str(attrdict, items):
            str_attrdict = str(attrdict)
            if not (str_attrdict.startswith('{')
                    and str_attrdict.endswith('}')):
                return False

            str_dict_items = ('%r: %r' % (key, value)
                              for key, value in items.items())
            return all(item in str_attrdict for item in str_dict_items)

        assert assert_attrdict_str(self.attrdict, {'a': 1, 'b': 2, 'c': 3})
        self.attrdict.pop('c')
        assert assert_attrdict_str(self.attrdict, {'a': 1, 'b': 2})

        assert str(AttributeDict()) == '{}'

    def test_repr(self):
        def assert_attrdict_repr(attrdict, items):
            attrdict_cls = type(attrdict).__name__
            repr_attrdict = repr(attrdict)
            if not (repr_attrdict.startswith(attrdict_cls + '({')
                    and repr_attrdict.endswith('})')):
                return False

            str_dict_items = ('%r: %r' % (key, value)
                              for key, value in items.items())
            return all(item in repr_attrdict for item in str_dict_items)

        assert assert_attrdict_repr(self.attrdict, {'a': 1, 'b': 2, 'c': 3})
        self.attrdict.pop('c')
        assert assert_attrdict_repr(self.attrdict, {'a': 1, 'b': 2})

        attrdict1 = AttributeDict()
        attrdict2 = AttributeDict({})
        assert repr(attrdict1) == repr(attrdict2) == 'AttributeDict()'
        assert abs(attrdict1) is not abs(attrdict2)

        attrdict3 = AttributeDict({'a': 1})
        assert assert_attrdict_repr(attrdict3, {'a': 1})
        attrdict3.pop('a')
        assert repr(attrdict3) == 'AttributeDict()'

    def test_dir(self):
        assert dir(self.attrdict) == sorted(list(self.attrdict))

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

    def test_noclobber(self):
        attrdict = AttributeDict()
        update_method = attrdict.update
        attrdict.update = 1
        assert attrdict.update == update_method
        assert attrdict['update'] == 1

        clear_method = attrdict.clear
        attrdict.update({'clear': 2})
        assert attrdict.clear == clear_method
        assert attrdict['clear'] == 2


class TestAttributeContainer(UnitTest):
    def setup_method(self):
        self.attrcon = AttributeContainer({'a': 1, 'b': 2, 'c': 3})
        self.attrcon_dict_nest = AttributeContainer({'a': {'b': 3}})

    def test_immutable(self):
        with pytest.raises(TypeError) as excinfo:
            self.attrcon.attr = 3
        assert 'immutable' in excinfo.value.args[0]

        with pytest.raises(TypeError) as excinfo:
            self.attrcon['attr'] = 3
        assert 'immutable' in excinfo.value.args[0]

        with pytest.raises(TypeError) as excinfo:
            del self.attrcon.attr
        assert 'immutable' in excinfo.value.args[0]

        with pytest.raises(TypeError) as excinfo:
            del self.attrcon['attr']
        assert 'immutable' in excinfo.value.args[0]

    def test_getitem(self):
        assert self.attrcon['a'] == 1

        with pytest.raises(KeyError):
            self.attrcon['z']

        assert type(self.attrcon_dict_nest['a']) is dict

    def test_getattr(self):
        assert self.attrcon.a == 1

        with pytest.raises(AttributeError):
            self.attrcon.z

        assert type(self.attrcon_dict_nest.a) is AttributeContainer

    def test_str(self):
        # Assert there is a __str__. This may not be in a pretty printed
        # format in some older Python versions.
        assert str(self.attrcon)


class TestRedditAttributes(UnitTest):
    def setup_method(self):
        self.redditattrs = RedditAttributes({'a': 1, 'b': {'c': 3}})

    def test_getitem(self):
        assert self.redditattrs['a'] == 1

        assert type(self.redditattrs['b']) is dict
        assert self.redditattrs['b'] == {'c': 3}

        with pytest.raises(KeyError):
            self.redditattrs['z']

    def test_getattr(self):
        assert type(self.redditattrs.b) is AttributeContainer
        assert self.redditattrs['b'] == AttributeContainer({'c': 3})
