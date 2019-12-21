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


class TestValidate(ValidateTester, UnitTest):
    def test_basic_yes(self):
        self.no_exception_test("12", str, variable_name="Twelve")

    def test_dict_yes(self):
        self.no_exception_test({}, dict, variable_name="data")

    def test_int_yes(self):
        self.no_exception_test(12, int, variable_name="comments")

    def test_sequence_yes(self):
        self.no_exception_test(
            (), collections.abc.Sequence, True, variable_name="TupleData"
        )

    def test_none_yes_true(self):
        self.no_exception_test(None, str, variable_name="ID")

    def test_grouped_yes(self):
        self.no_exception_test("test", (str, list), variable_name="TestData")
        self.no_exception_test(
            ["test"], (str, list), variable_name="TestData2"
        )

    def test_none_yes_false(self):
        self.no_exception_test(None, None, ignore_none=False, variable_name="NoneTest")

    def test_none_yes_false_grouped(self):
        self.no_exception_test(None, (str, None), ignore_none=False, variable_name="NoneTest")

    def test_internal_call_yes_mismatch_arg3(self):
        self.no_exception_test(None, int, _internal_call={}, variable_name="test")

    def test_internal_call_yes_mismatch_arg4(self):
        self.no_exception_test(None, int, _internal_call=True, variable_name=3)

    def test_internal_call_yes_mismatch_arg5(self):
        self.no_exception_test(
            None,
            int,
            expected_type_names={},
            _internal_call=True,
            variable_name="Test",
        )

    def test_internal_call_yes_mismatch_arg6(self):
        self.no_exception_test(
            None,
            int,
            error_message={},
            _internal_call=True,
            variable_name="Test",
        )

    def test_internal_call_yes_mismatch_arg7_invalid_type(self):
        self.no_exception_test(
            None,
            int,
            error_class=12,
            _internal_call=True,
            variable_name="Test",
        )

    def test_internal_call_yes_mismatch_arg7_nonerror_class(self):
        self.no_exception_test(
            None,
            int,
            error_class=str,
            _internal_call=True,
            variable_name="Test",
        )

    def test_internal_call_yes_arg2_int(self):
        self.no_exception_test(None, int, ignore_none=1, variable_name="Test")

    class FauxError(Exception):
        """An exception class that is user made (not builtin) for error checking"""

    def test_msg_magic(self):
        self.check_msg(
            "The variable 'id' must be type `str` (was type `int`).",
            12,
            str,
            variable_name="id",
        )

    def test_msg_using_custom_class(self):
        self.check_msg(
            "The variable 'id' must be type `FauxError` (was type `int`).",
            12,
            self.FauxError,
            variable_name="id",
        )

    def test_msg_using_alt_builtin_class(self):
        self.check_msg(
            "The variable 'id' must be type `str` (was type `int`).",
            12,
            str,
            variable_name="id",
            error_class=ValueError,
        )

    def test_msg_omit_variable_name_no_error_message(self):
        self.check_msg(
            "variable_name needs to be specified if error_message is not given",
            12,
            str,
            catch_class=ValueError
        )

    def test_msg_grouped(self):
        self.check_msg(
            "The variable 'id' must be types `str`, `list` or `dict` (was type `int`).",
            12,
            (str, list, dict),
            variable_name="id",
        )

    def test_msg_invalid_expected_types(self):
        self.check_msg(
            "The variable 'expected_types' must be types `type`, `list`, `tuple` or `set` (was type `dict`).",
            12,
            {str: int},
            variable_name="id",
        )

    def test_msg_invalid_variable_name(self):
        self.check_msg(
            "The variable 'variable_name' must be type `str` (was type `int`).",
            12,
            str,
            variable_name=14,
        )

    def test_msg_custom_error_message_no_vars(self):
        self.check_msg("1+1=2", 12, str, error_message="1+1=2")

    def test_msg_invalid_ignore_none(self):
        self.check_msg(
            "The variable 'ignore_none' must be types `int` or `bool` (was type `float`).",
            "12",
            str,
            ignore_none=3.3,
            variable_name="id",
        )

    def test_msg_double_error_message_and_variable_name(self):
        self.check_msg(
            "Both error_message and variable_name has been specified. Please only specify one.",
            "12",
            str,
            variable_name="id",
            error_message="Hi",
            catch_class=ValueError,
        )

    def test_msg_invalid_expected_type_names(self):
        self.check_msg(
            "The variable 'expected_type_names' must be types `str`, `list`, `tuple`,"
            " `set` or `type` (was type `int`).",
            "12",
            str,
            variable_name="id",
            expected_type_names=5,
        )

    def test_msg_custom_error_with_vars(self):
        self.check_msg(
            "WRONG TYPES, NAME: test, EXPECTED: `int` or `float`, GOT: `str`",
            "12",
            (int, float),
            variable_name="test",
            error_message="WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s",
        )

    def test_msg_custom_error_with_variables_and_other_builtin_class(self):
        self.check_msg(
            "WRONG TYPES, NAME: test, EXPECTED: `int` or `float`, GOT: `str`",
            "12",
            (int, float),
            variable_name="test",
            error_message="WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s",
            error_class=ValueError,
        )

    def test_msg_custom_error_with_variables_and_missing_variable_name(self):
        self.check_msg(
            "variable_name needs to be specified if error_message contains the correct amount of string "
            "substitution modifiers.",
            "12",
            (int, float, bool),
            error_message="1: %s, 2: %s, 3: %s",
            catch_class=ValueError
        )

    def test_msg_custom_error_with_variables_and_custom_expected_type_names(
        self,
    ):
        self.check_msg(
            "WRONG TYPES, NAME: test, EXPECTED: `One`, `Two` or `Three`, GOT: `str`",
            "12",
            (int, float),
            variable_name="test",
            error_message="WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s",
            expected_type_names=["One", "Two", "Three"],
        )

    def test_msg_expected_type_names_is_string(self):
        self.check_msg(
            "The variable 'id' must be type `str` (was type `int`).",
            12,
            str,
            variable_name="id",
            expected_type_names="str",
        )

    def test_msg_expected_type_names_is_type(self):
        self.check_msg(
            "The variable 'id' must be type `str` (was type `int`).",
            12,
            str,
            variable_name="id",
            expected_type_names=str,
        )

    def test_msg_expected_type_names_is_list_of_strings_and_types(self):
        self.check_msg(
            "The variable 'id' must be type `str` or `string` (was type `int`).",
            12,
            str,
            variable_name="id",
            expected_type_names=[str, "string"],
        )

    def test_msg_internal_call_mismatch_arg2(self):
        self.check_msg("isinstance() arg 2 must be a type or tuple of types",
            None, {int: dict}, _internal_call=True, variable_name="Test"
        )
