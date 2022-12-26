"""This file should be updated as files/classes/functions are deprecated."""
import inspect
from contextlib import contextmanager

import pytest

from praw.util import _deprecate_args  # noqa

from .. import UnitTest

keyword_only = {
    "args": [
        [("arg2", "arg1", "arg3", "arg0"), dict()],
        ("arg0", "arg1", "arg2", "arg3"),
    ],
    "kwargs": [
        [(), dict(arg2="arg2", arg1="arg1", arg3="arg3", arg0="arg0")],
        ("arg0", "arg1", "arg2", "arg3"),
    ],
    "mix": [
        [("arg2",), dict(arg1="arg1")],
        (None, "arg1", "arg2", None),
    ],
    "one_arg": [
        [("arg2",), dict()],
        (None, None, "arg2", None),
    ],
    "one_kwarg": [
        [(), dict(arg0="arg0")],
        ("arg0", None, None, None),
    ],
}
with_positional = {
    "args": [
        [("arg0", "arg2", "arg1", "arg3"), dict()],
        ("arg0", "arg1", "arg2", "arg3"),
    ],
    "kwargs": [
        [("arg0",), dict(arg2="arg2", arg1="arg1", arg3="arg3")],
        ("arg0", "arg1", "arg2", "arg3"),
    ],
    "mix": [
        [("arg0", "arg2"), dict(arg1="arg1", arg3=None)],
        ("arg0", "arg1", "arg2", None),
    ],
    "one_arg": [
        [("arg0",), dict()],
        ("arg0", None, None, None),
    ],
    "one_kwarg": [
        [(), dict(arg0="arg0")],
        ("arg0", None, None, None),
    ],
}


@contextmanager
def _check_warning(func, args):
    if args:
        with pytest.warns(DeprecationWarning, match=_gen_warning(func, args)):
            yield
    else:
        yield


def _gen_warning(func, args):
    arg_list = list(map(repr, args))
    arg_count = len(args)
    plural = arg_count > 1
    arg_string = (
        " and ".join(arg_list)
        if arg_count < 3
        else f"{', '.join(arg_list[:-1])}, and {arg_list[-1]}"
    )
    arg_string += f" as {'' if plural else 'a '}"
    arg_string += f"keyword argument{'s' if plural else ''}"
    return (
        f"Positional arguments for {func.__qualname__!r} will no longer be supported in"
        f" PRAW 8.\nCall this function with {arg_string}."
    )


def _prepare_args(arguments, func):
    args, kwargs = arguments
    parameters = inspect.signature(func).parameters.values()
    check_args = args[
        len(
            [
                param
                for param in parameters
                if param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
            ]
        ) :
    ]
    return args, check_args, kwargs


@_deprecate_args("arg2", "arg1", "arg3", "arg0")
def arg_test_global(*, arg0=None, arg1=None, arg2=None, arg3=None):
    return arg0, arg1, arg2, arg3


@_deprecate_args("arg0", "arg2", "arg1", "arg3")
def arg_test_global_with_positional(arg0, *, arg1=None, arg2=None, arg3=None):
    return arg0, arg1, arg2, arg3


def pytest_generate_tests(metafunc):
    # called once per each test function
    positional = "positional" in metafunc.function.__name__
    test_cases = metafunc.cls.params["positional" if positional else "keyword"]
    name = "_".join(metafunc.function.__name__.split("_")[1:])
    cases = []
    ids = []
    for test_case, parameters in test_cases.items():
        arguments, expected_results = parameters
        cases.append([arguments, expected_results, name])
        ids.append(test_case)
    signature = inspect.signature(metafunc.function)
    args = [arg.name for arg in signature.parameters.values() if arg.name != "self"]
    metafunc.parametrize(argnames=args, argvalues=cases, ids=ids)


class ArgTest:
    @_deprecate_args("arg2", "arg1", "arg3", "arg0")
    def arg_test(self, *, arg0=None, arg1=None, arg2=None, arg3=None):
        return arg0, arg1, arg2, arg3

    @_deprecate_args("arg0", "arg2", "arg1", "arg3")
    def arg_test_with_positional(self, arg0, *, arg1=None, arg2=None, arg3=None):
        return arg0, arg1, arg2, arg3


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecateArgs(UnitTest):
    @pytest.fixture(autouse=True)
    def arg_test(self):
        self.arg_test = ArgTest()

    params = {
        "keyword": keyword_only,
        "positional": with_positional,
    }

    def _execute_test(self, arguments, expected_results, func_name):
        if "global" in func_name:
            func = globals()[func_name]
        else:
            func = getattr(self.arg_test, func_name)
        args, check_args, kwargs = _prepare_args(arguments, func)
        with _check_warning(func, check_args):
            results = func(*args, **kwargs)
        assert expected_results == results

    def test_arg_test(self, arguments, expected_result, func_name):
        self._execute_test(arguments, expected_result, func_name)

    def test_arg_test_global(self, arguments, expected_result, func_name):
        self._execute_test(arguments, expected_result, func_name)

    def test_arg_test_global_with_positional(
        self, arguments, expected_result, func_name
    ):
        self._execute_test(arguments, expected_result, func_name)

    def test_arg_test_with_positional(self, arguments, expected_result, func_name):
        self._execute_test(arguments, expected_result, func_name)
