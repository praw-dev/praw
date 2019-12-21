from praw.util.validate_types import (
    validate_types,
    validate_url,
    validate_id,
    _remove_extra_attrs,
)

from .test_validate_types import ValidateTester

from ... import UnitTest


class TestValidateDefaults(ValidateTester):
    """Base class that provides checking defaults."""

    @classmethod
    def no_exception_test(
        cls,
        variable,
        ignore_none=True,
        call_function=validate_types,
        **parent_kwargs
    ):
        return super().no_exception_test(
            variable,
            call_function=call_function,
            ignore_none=ignore_none,
            **_remove_extra_attrs(parent_kwargs)
        )

    @classmethod
    def check_msg(
        cls,
        msg,
        variable,
        ignore_none=True,
        call_function=validate_types,
        **parent_kwargs
    ):
        return super().check_msg(
            msg,
            variable,
            call_function=call_function,
            ignore_none=ignore_none,
            **_remove_extra_attrs(parent_kwargs)
        )

    def _validate_correct_id(self):
        assert self.no_exception_test("12")
        assert self.no_exception_test(None)

    def _validate_incorrect_id(self):
        assert not self.no_exception_test(12)
        assert not self.no_exception_test([])
        assert not self.no_exception_test({})
        assert not self.no_exception_test(object())
        assert not self.no_exception_test(type)

    def _validate_no_none(self, variable_name):
        assert not self.no_exception_test(None, ignore_none=False)
        assert self.check_msg(
            "The variable '%s' must be type `str` "
            "(was type `NoneType`)." % variable_name,
            None,
            ignore_none=False,
        )

    def _validate_correct_msg(self, variable_name):
        assert self.check_msg(
            "The variable '%s' must be type `str` "
            "(was type `int`)." % variable_name,
            12,
        )
        assert self.check_msg(
            "The variable '%s' must be type `str` ("
            "was type `list`)." % variable_name,
            [],
        )
        assert self.check_msg(
            "The variable '%s' must be type `str` "
            "(was type `dict`)." % variable_name,
            {},
        )
        assert self.check_msg(
            "The variable '%s' must be type `str` "
            "(was type `object`)." % variable_name,
            object(),
        )
        assert self.check_msg(
            "The variable '%s' must be type `str` "
            "(was type `type`)." % variable_name,
            type,
        )

    def _validate_incorrect_msg(self):
        assert not self.check_msg("Object() hash: 286212504", 12)

    def _validate_custom_args(self):
        set1 = {"expected_type_names": "string", "error_message": "%s %s %s"}
        set2 = {"_internal_call": True, "expected_type_names": 1}
        assert self.no_exception_test("12", **set1)
        assert self.no_exception_test("12", **set2)


class TestValidateID(TestValidateDefaults, UnitTest):
    @classmethod
    def no_exception_test(
        cls,
        variable,
        ignore_none=True,
        call_function=validate_id,
        **parent_kwargs
    ):
        return super().no_exception_test(
            variable, ignore_none, call_function, **parent_kwargs
        )

    @classmethod
    def check_msg(
        cls,
        msg,
        variable,
        ignore_none=True,
        call_function=validate_id,
        **parent_kwargs
    ):
        return super().check_msg(
            msg, variable, ignore_none, call_function, **parent_kwargs
        )

    def test_validate_no_none(self, *_args, **__kwargs):
        self._validate_no_none("id")

    def test_validate_correct_msg(self, *_args, **__kwargs):
        self._validate_correct_msg("id")

    def test_validate_correct_id(self):
        self._validate_correct_id()

    def test_validate_incorrect_id(self):
        self._validate_incorrect_id()

    def test_validate_incorrect_msg(self):
        self._validate_incorrect_msg()

    def test_validate_custom_args(self):
        self._validate_custom_args()


class TestValidateURL(TestValidateDefaults, UnitTest):
    @classmethod
    def no_exception_test(
        cls,
        variable,
        ignore_none=True,
        call_function=validate_url,
        **parent_kwargs
    ):
        return super().no_exception_test(
            variable, ignore_none, call_function, **parent_kwargs
        )

    def test_validate_correct_id(self):
        self._validate_correct_id()

    def test_validate_incorrect_id(self):
        self._validate_incorrect_id()

    def test_validate_incorrect_msg(self):
        self._validate_incorrect_msg()

    def test_validate_custom_args(self):
        self._validate_custom_args()

    @classmethod
    def check_msg(
        cls,
        msg,
        variable,
        ignore_none=True,
        call_function=validate_url,
        **parent_kwargs
    ):
        return super().check_msg(
            msg, variable, ignore_none, call_function, **parent_kwargs
        )

    def test_validate_no_none(self, *_args, **__kwargs):
        self._validate_no_none("url")

    def test_validate_correct_msg(self, *_args, **__kwargs):
        self._validate_correct_msg("url")
