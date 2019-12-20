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
                  expected_type_names=None, error_message=None, error_class=TypeError):
        with pytest.raises(error_class) as exc:
            validate_types(variable, expected_types, ignore_none=ignore_none, _internal_call=_internal_call,
                           variable_name=variable_name, expected_type_names=expected_type_names,
                           error_message=error_message, error_class=error_class)
        assert exc.value.args[0] == msg

    @staticmethod
    def assert_error_validate(variable, expected_types, ignore_none=True, _internal_call=False, variable_name=None,
                              expected_type_names=None, error_message=None, error_class=TypeError):
        with pytest.raises(error_class):
            validate_types(variable, expected_types, ignore_none=ignore_none, _internal_call=_internal_call,
                           variable_name=variable_name, expected_type_names=expected_type_names,
                           error_message=error_message, error_class=error_class)


# noinspection PyTypeChecker
class TestValidate(ValidateTester, UnitTest):
    def test_expected(self):
        self.no_exception_test("12", str, variable_name="Twelve")
        self.no_exception_test(12, int, variable_name='comments')
        self.no_exception_test({}, dict, variable_name='data')
        self.no_exception_test((), collections.abc.Sequence, True, variable_name='TupleData')
        self.no_exception_test(None, str, variable_name='ID')
        self.no_exception_test('test', (str, list), variable_name='TestData')
        self.no_exception_test(['test'], (str, list), variable_name='TestData2')
        self.no_exception_test(None, None, ignore_none=False, variable_name="NoneTest")
        self.no_exception_test(None, {int: dict}, _internal_call=True, variable_name="Test")
        self.no_exception_test(None, int, _internal_call=True, variable_name=3)
        self.no_exception_test(None, int, ignore_none=1, variable_name="Test")

    class FauxError(Exception):
        """An exception class that is user made (not builtin) for error checking"""

        def __init__(self, *args):
            super(self, TestValidate.FauxError).__init__(*args)

    def test_unexpected(self):
        self.assert_error_validate(12, str, variable_name="ID")
        self.assert_error_validate(12, collections.abc.Sequence, variable_name="Test")
        self.assert_error_validate(["12"], str, variable_name="ID")
        self.assert_error_validate({"id": "12"}, list, variable_name="ID")
        self.assert_error_validate(12, str, variable_name="ID", error_class=ValueError)
        self.assert_error_validate(12, str, variable_name="ID", error_class=self.FauxError)
        self.assert_error_validate(12, str, variable_name="ID", expected_type_names=12)
        self.assert_error_validate(None, str, variable_name="ID", ignore_none=False)
        self.assert_error_validate(None, str, ignore_none=True)
        self.assert_error_validate(12, {str: int}, variable_name="id")
        self.assert_error_validate(12, type, variable_name="id_type", expected_type_names={1: 2})
        self.assert_error_validate("12", str, variable_name=1)
        self.assert_error_validate("12", str, variable_name="id", error_message=4)
        self.assert_error_validate("12", str, variable_name="id", error_class=4)
        self.assert_error_validate("12", str, ignore_none=4.4, variable_name="id")

    def test_messages(self):
        self.check_msg("The variable 'id' must be type `str` (was type `int`).", 12, str, variable_name="id")
        self.check_msg("The variable 'id' must be type `FauxError` (was type `int`).", 12, self.FauxError,
                       variable_name="id")
        self.check_msg("The variable 'id' must be type `str` (was type `int`).", 12, str, variable_name="id",
                       error_class=ValueError)
        self.check_msg("variable_name needs to be specified if error_message is not given", 12, str)
        self.check_msg("The variable 'id' must be types `str`, `list`, or `dict` (was type `int`).", 12,
                       (str, list, dict), variable_name="id")
        self.check_msg("The variable 'expected_types' must be types `str`, `list`, `tuple`, or `set` (was type `dict`).",
                       12, {str: int}, variable_name="id")
        self.check_msg("The variable 'variable_name 'must be type `str` (was type `int`).", 12, str, variable_name=14)
        self.check_msg("1+1=2", 12, str, error_message="1+1=2")
        self.check_msg("The variable 'ignore_none' must be types `int` or `bool` (was type `float`).", "12", str,
                       ignore_none=3.3, variable_name="id")
