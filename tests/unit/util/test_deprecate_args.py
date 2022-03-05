"""This file should be updated as files/classes/functions are deprecated."""
import pytest

from praw.util import _deprecate_args

from .. import UnitTest


@_deprecate_args("arg2", "arg1", "arg3", "arg0")
def arg_test_global(*, arg0=None, arg1=None, arg2=None, arg3=None):
    return arg0, arg1, arg2, arg3


@_deprecate_args("arg0", "arg2", "arg1", "arg3")
def arg_test_global_with_positional(arg0, *, arg1=None, arg2=None, arg3=None):
    return arg0, arg1, arg2, arg3


class ArgTest:
    @_deprecate_args("arg2", "arg1", "arg3", "arg0")
    def arg_test(self, *, arg0=None, arg1=None, arg2=None, arg3=None):
        return arg0, arg1, arg2, arg3

    @_deprecate_args("arg0", "arg2", "arg1", "arg3")
    def arg_test_with_positional(self, arg0, *, arg1=None, arg2=None, arg3=None):
        return arg0, arg1, arg2, arg3


class TestDeprecateArgs(UnitTest):
    def setup(self):
        self.arg_test = ArgTest()

    def test_arg_test(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'ArgTest.arg_test' will no longer be"
                " supported in PRAW 8.\nCall this function with 'arg2', 'arg1', 'arg3',"
                " and 'arg0' as keyword arguments."
            ),
        ):
            result_args = self.arg_test.arg_test("arg2", "arg1", "arg3", "arg0")
            assert result_args == ("arg0", "arg1", "arg2", "arg3")

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test__keyword(self):
        result_args = self.arg_test.arg_test(
            arg2="arg2", arg1="arg1", arg3="arg3", arg0="arg0"
        )
        assert result_args == ("arg0", "arg1", "arg2", "arg3")

    def test_arg_test__mix(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'ArgTest.arg_test' will no longer be"
                " supported in PRAW 8.\nCall this function with 'arg2' as a keyword"
                " argument."
            ),
        ):
            result_args = self.arg_test.arg_test("arg2", arg1="arg1")
            assert result_args == (None, "arg1", "arg2", None)

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test__one_keyword(self):
        result_args = self.arg_test.arg_test(arg0="arg0")
        assert result_args == ("arg0", None, None, None)

    def test_arg_test__one_positional(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'ArgTest.arg_test' will no longer be"
                " supported in PRAW 8.\nCall this function with 'arg2' as a keyword"
                " argument."
            ),
        ):
            result_args = self.arg_test.arg_test("arg2")
            assert result_args == (None, None, "arg2", None)

    def test_arg_test_global(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'arg_test_global' will no longer be supported"
                " in PRAW 8.\nCall this function with 'arg2', 'arg1', 'arg3', and"
                " 'arg0' as keyword arguments."
            ),
        ):
            result_args = arg_test_global("arg2", "arg1", "arg3", "arg0")
            assert result_args == ("arg0", "arg1", "arg2", "arg3")

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_global__keyword(self):
        result_args = arg_test_global(
            arg2="arg2", arg1="arg1", arg3="arg3", arg0="arg0"
        )
        assert result_args == ("arg0", "arg1", "arg2", "arg3")

    def test_arg_test_global__mix(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'arg_test_global' will no longer be supported"
                " in PRAW 8.\nCall this function with 'arg2' as a keyword argument."
            ),
        ):
            result_args = arg_test_global("arg2", arg1="arg1")
            assert result_args == (None, "arg1", "arg2", None)

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_global__one_keyword(self):
        result_args = arg_test_global(arg0="arg0")
        assert result_args == ("arg0", None, None, None)

    def test_arg_test_global__one_positional(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'arg_test_global' will no longer be supported"
                " in PRAW 8.\nCall this function with 'arg2' as a keyword argument."
            ),
        ):
            result_args = arg_test_global("arg2")
            assert result_args == (None, None, "arg2", None)

    def test_arg_test_global_with_positional(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'arg_test_global_with_positional' will no"
                " longer be supported in PRAW 8.\nCall this function with 'arg2',"
                " 'arg1', and 'arg3' as keyword arguments."
            ),
        ):
            result_args = arg_test_global_with_positional(
                "arg0", "arg2", "arg1", "arg3"
            )
            assert result_args == ("arg0", "arg1", "arg2", "arg3")

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_global_with_positional__keyword(self):
        result_args = arg_test_global_with_positional(
            arg0="arg0", arg2="arg2", arg1="arg1", arg3="arg3"
        )
        assert result_args == ("arg0", "arg1", "arg2", "arg3")

    def test_arg_test_global_with_positional__mix(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'arg_test_global_with_positional' will no"
                " longer be supported in PRAW 8.\nCall this function with 'arg2' and"
                " 'arg1' as keyword arguments."
            ),
        ):
            result_args = arg_test_global_with_positional(
                "arg0", "arg2", "arg1", arg3=None
            )
            assert result_args == ("arg0", "arg1", "arg2", None)

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_global_with_positional__one_keyword(self):
        result_args = arg_test_global_with_positional("arg0", arg1="arg1")
        assert result_args == ("arg0", "arg1", None, None)

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_global_with_positional__one_positional(self):
        result_args = arg_test_global_with_positional("arg0")
        assert result_args == ("arg0", None, None, None)

    def test_arg_test_with_positional(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'ArgTest.arg_test_with_positional' will no"
                " longer be supported in PRAW 8.\nCall this function with 'arg2',"
                " 'arg1', and 'arg3' as keyword arguments."
            ),
        ):
            result_args = self.arg_test.arg_test_with_positional(
                "arg0", "arg2", "arg1", "arg3"
            )
            assert result_args == ("arg0", "arg1", "arg2", "arg3")

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_with_positional__keyword(self):
        result_args = self.arg_test.arg_test_with_positional(
            arg0="arg0", arg2="arg2", arg1="arg1", arg3="arg3"
        )
        assert result_args == ("arg0", "arg1", "arg2", "arg3")

    def test_arg_test_with_positional__mix(self):
        with pytest.warns(
            DeprecationWarning,
            match=(
                "Positional arguments for 'ArgTest.arg_test_with_positional' will no"
                " longer be supported in PRAW 8.\nCall this function with 'arg2' as a"
                " keyword argument."
            ),
        ):
            result_args = self.arg_test.arg_test_with_positional(
                "arg0", "arg2", arg1="arg1", arg3=None
            )
            assert result_args == ("arg0", "arg1", "arg2", None)

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_with_positional__one_keyword(self):
        result_args = self.arg_test.arg_test_with_positional("arg0", arg1="arg1")
        assert result_args == ("arg0", "arg1", None, None)

    @pytest.mark.filterwarnings("error", category=DeprecationWarning)
    def test_arg_test_with_positional__one_positional(self):
        result_args = self.arg_test.arg_test_with_positional("arg0")
        assert result_args == ("arg0", None, None, None)
