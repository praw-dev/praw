import collections

import pytest

from praw.util.validate_types import validate_types
from .. import UnitTest


class ValidateTester:
    @staticmethod
    def no_exception_test(
        variable,
        expected_types,
        ignore_none=True,
        _internal_call=False,
        variable_name=None,
        expected_type_names=None,
        error_message=None,
        error_class=TypeError,
    ):
        try:
            validate_types(
                variable,
                expected_types,
                ignore_none=ignore_none,
                _internal_call=_internal_call,
                variable_name=variable_name,
                expected_type_names=expected_type_names,
                error_message=error_message,
                error_class=error_class,
            )
        except error_class:
            assert False
        else:
            assert True

    @staticmethod
    def check_msg(
        msg,
        variable,
        expected_types,
        ignore_none=True,
        _internal_call=False,
        variable_name=None,
        expected_type_names=None,
        error_message=None,
        error_class=TypeError,
        catch_class=None,
    ):
        if catch_class is None:
            catch_class = error_class
        with pytest.raises(catch_class) as exc:
            validate_types(
                variable,
                expected_types,
                ignore_none=ignore_none,
                _internal_call=_internal_call,
                variable_name=variable_name,
                expected_type_names=expected_type_names,
                error_message=error_message,
                error_class=error_class,
            )
        assert exc.value.args[0] == msg

    @staticmethod
    def assert_error_validate(
        variable,
        expected_types,
        ignore_none=True,
        _internal_call=False,
        variable_name=None,
        expected_type_names=None,
        error_message=None,
        error_class=TypeError,
        catch_class=None,
    ):
        if catch_class is None:
            catch_class = error_class
        with pytest.raises(catch_class):
            validate_types(
                variable,
                expected_types,
                ignore_none=ignore_none,
                _internal_call=_internal_call,
                variable_name=variable_name,
                expected_type_names=expected_type_names,
                error_message=error_message,
                error_class=error_class,
            )


# noinspection PyTypeChecker
class TestValidate(ValidateTester, UnitTest):
    def test_expected(self):
        self.no_exception_test("12", str, variable_name="Twelve")
        self.no_exception_test(12, int, variable_name="comments")
        self.no_exception_test({}, dict, variable_name="data")
        self.no_exception_test(
            (), collections.abc.Sequence, True, variable_name="TupleData"
        )
        self.no_exception_test(None, str, variable_name="ID")
        self.no_exception_test("test", (str, list), variable_name="TestData")
        self.no_exception_test(
            ["test"], (str, list), variable_name="TestData2"
        )
        self.no_exception_test(
            None, None, ignore_none=False, variable_name="NoneTest"
        )
        self.no_exception_test(
            None, {int: dict}, _internal_call=True, variable_name="Test"
        )
        self.no_exception_test(None, int, _internal_call=True, variable_name=3)
        self.no_exception_test(None, int, ignore_none=1, variable_name="Test")

    class FauxError(Exception):
        """An exception class that is user made (not builtin) for error checking"""

        def __init__(self, *args):
            super(self, TestValidate.FauxError).__init__(*args)

    def test_messages(self):
        self.check_msg(
            "The variable 'id' must be type `str` (was type `int`).",
            12,
            str,
            variable_name="id",
        )
        self.check_msg(
            "The variable 'id' must be type `FauxError` (was type `int`).",
            12,
            self.FauxError,
            variable_name="id",
        )
        self.check_msg(
            "The variable 'id' must be type `str` (was type `int`).",
            12,
            str,
            variable_name="id",
            error_class=ValueError,
        )
        self.check_msg(
            "variable_name needs to be specified if error_message is not given",
            12,
            str,
        )
        self.check_msg(
            "The variable 'id' must be types `str`, `list`, or `dict` (was type `int`).",
            12,
            (str, list, dict),
            variable_name="id",
        )
        self.check_msg(
            "The variable 'expected_types' must be types `str`, `list`, `tuple`, or `set` (was type `dict`).",
            12,
            {str: int},
            variable_name="id",
        )
        self.check_msg(
            "The variable 'variable_name 'must be type `str` (was type `int`).",
            12,
            str,
            variable_name=14,
        )
        self.check_msg("1+1=2", 12, str, error_message="1+1=2")
        self.check_msg(
            "The variable 'ignore_none' must be types `int` or `bool` (was type `float`).",
            "12",
            str,
            ignore_none=3.3,
            variable_name="id",
        )
        self.check_msg(
            "Both error_message and variable_name has been specifed. Please only specify one.",
            "12",
            str,
            variable_name="id",
            error_message="Hi",
            catch_class=ValueError,
        )
        self.check_msg(
            "The variable 'expected_type_names' must be types `str`, `list`, `tuple`,"
            " `set` or `type` (was type `int`).",
            "12",
            str,
            variable_name="id",
            expected_type_names=5,
        )
        self.check_msg(
            "WRONG TYPES, NAME: test, EXPECTED: `int` or `float`, GOT: `str`",
            "12",
            (int, float),
            variable_name="test",
            error_message="WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s",
        )
        self.check_msg(
            "WRONG TYPES, NAME: test, EXPECTED: `int` or `float`, GOT: `str`",
            "12",
            (int, float),
            variable_name="test",
            error_message="WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s",
            error_class=ValueError,
        )
        self.check_msg(
            "variable_name needs to be specified if error_message contains the correct amount of string "
            "substitution modifiers.",
            "12",
            (int, float, bool),
            error_message="1: %s, 2: %s, 3: %s",
        )
        self.check_msg(
            "WRONG TYPES, NAME: test, EXPECTED: `One`, `Two` or `Three`, GOT: `str`",
            "12",
            (int, float),
            variable_name="test",
            error_message="WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s",
            expected_type_names=["One", "Two", "Three"],
        )
