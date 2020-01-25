"""Provide the ExportableMixin class."""
from json import dumps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from ..base import RedditBase

_T = TypeVar("_T")
Reddit = TypeVar("Reddit")


class ExportableMixin:
    """A mixin for classes that can be easily exported and re-created."""

    @staticmethod
    def _create_base(
        base: Callable[
            [Reddit, str, Dict[str, Union[Any, Dict[str, Any]]]], _T
        ],
        reddit: Reddit,
        data: Union[str, Dict[str, Union[Any, Dict[str, Any]]]],
    ) -> _T:
        """Create another PRAWBase with either a string or a dict."""
        return (
            base(reddit, _data=data)
            if isinstance(data, dict)
            else base(reddit, data)
        )

    @classmethod
    def _expand_value(
        cls,
        value: Union[Dict[str, Any], List[Any]],
        remove_private,
        stringify,
        _internal_counter=0,
    ):
        if _internal_counter >= 3:
            return value
        if hasattr(value, "export") and not stringify:
            value = value.export(
                remove_private=remove_private,
                _internal_counter=_internal_counter + 1,
            )
        elif isinstance(value, RedditBase) and stringify:
            value = str(value)
        elif isinstance(value, dict):
            for key, subvalue in value.copy().items():
                value[key] = cls._expand_value(
                    subvalue,
                    remove_private,
                    stringify,
                    _internal_counter=_internal_counter + 1,
                )
        elif isinstance(value, (list, tuple)):
            value = list(value)
            for index, item in enumerate(value):
                value[index] = cls._expand_value(
                    item,
                    remove_private,
                    stringify,
                    _internal_counter=_internal_counter + 1,
                )

        return value

    @classmethod
    def _jsonify_base(
        cls, base: Union[Dict[str, Any], List[Any]], _internal_counter=0
    ):
        if isinstance(base, dict):
            # removes non-json from dicts
            for key, value in base.copy().items():
                if not (
                    isinstance(
                        value, (dict, list, tuple, str, int, float, bool)
                    )
                    or value is None
                ):
                    print(base.keys(), key, value)
                    base.pop(key, None)
                if isinstance(value, (dict, list, tuple)):
                    if _internal_counter < 3:
                        base[key] = cls._jsonify_base(
                            value, _internal_counter=_internal_counter + 1
                        )
                    else:
                        base.pop(key, None)
        if isinstance(base, (list, tuple)):
            # removes non-json from lists and tuples
            base = list(base)
            for index, item in enumerate(base):
                if not (
                    isinstance(
                        item, (dict, list, tuple, str, int, float, bool)
                    )
                    or item is None
                ):
                    base.pop(index, None)
                if isinstance(item, (dict, list, tuple)):
                    if _internal_counter < 3:
                        base[index] = cls._jsonify_base(
                            item, _internal_counter=_internal_counter + 1
                        )
                    else:

                        base.pop(index, None)
        return base

    def export(
        self,
        jsonify: bool = False,
        remove_private: Optional[bool] = None,
        stringify: bool = False,
        _internal_counter: int = 0,
    ) -> Union[Dict[str, Union[Any, Dict[str, Any]]], str]:
        """Export the data of the class, as a dict of the attributes.

        Other ExportableMixin classes are exported as dicts.

        The exported data should be able to re-create a copy of the class
        that is identical to the class the data was exported from.

        :param jsonify: Convert the exported dict into JSON. This will remove
            all objects that cannot be converted into json. Will return a
            string containing the dict. Using jsonify will also set
            parameter ``remove_private`` to True unless explicitly set to
            False. (Default: False)
        :param remove_private: Removes all attributes that begin with `_`.
            (Default: None).
        :param stringify: Convert RedditBases to strings instead of exporting
            them (Default: False)
        :returns: A dict of the attributes that got exported, or a string
            containing the dict.
        """
        if remove_private is None:
            remove_private = True if jsonify else False
        base = {}
        for key, value in self.__dict__.items():
            # private removal run
            if remove_private and key.startswith("_"):
                continue
            base[key] = self._expand_value(
                value,
                remove_private,
                stringify,
                _internal_counter=_internal_counter,
            )
        if jsonify:
            base = self._jsonify_base(base)
            return dumps(base, ensure_ascii=False)
        return base
