"""Test praw.models.util."""
import collections

import pytest

from praw.models.util import ExponentialCounter, permissions_string, validate_types
from .. import UnitTest


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
        assert "-all,+d" == permissions_string(["d"], set())
        assert "-all,-a,-b,-c,+d" == permissions_string(
            ["d"], self.PERMISSIONS
        )


class ValidateTester:
    @staticmethod
    def no_exception_test(variable, expected_types, ignore_none=True, _internal_call=False, variable_name=None,
                          expected_type_names=None, error_message=None, error_class=TypeError):
        try:
            validate_types(variable, expected_types, ignore_none=ignore_none, _internal_call=_internal_call,
                           variable_name=variable_name, expected_type_names=expected_type_names,
                           error_message=error_message, error_class=error_class)
        except error_class:
            assert False
        else:
            assert True

    @staticmethod
    def check_msg(msg, variable, expected_types, ignore_none=True, _internal_call=False, variable_name=None,
                  expected_type_names=None, error_message=None, error_class=TypeError, catch_class=None):
        if catch_class is None:
            catch_class = error_class
        with pytest.raises(catch_class) as exc:
            validate_types(variable, expected_types, ignore_none=ignore_none, _internal_call=_internal_call,
                           variable_name=variable_name, expected_type_names=expected_type_names,
                           error_message=error_message, error_class=error_class)
        assert exc.value.args[0] == msg

    @staticmethod
    def assert_error_validate(variable, expected_types, ignore_none=True, _internal_call=False, variable_name=None,
                              expected_type_names=None, error_message=None, error_class=TypeError, catch_class=None):
        if catch_class is None:
            catch_class = error_class
        with pytest.raises(catch_class):
            validate_types(variable, expected_types, ignore_none=ignore_none, _internal_call=_internal_call,
                           variable_name=variable_name, expected_type_names=expected_type_names,
                           error_message=error_message, error_class=error_class)
