"""Provide the ExportableMixin class."""
from typing import Any, Callable, Dict, TypeVar, Union

_T = TypeVar("_T")
Reddit = TypeVar("Reddit")


class ExportableMixin:
    """A mixin for classes that can be easily exported and re-created."""

    @staticmethod
    def _create_base(
        base: Callable[
            [Reddit, Union[str, Dict[str, Union[Any, Dict[str, Any]]]]], _T
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

    def export(self) -> Dict[str, Union[Any, Dict[str, Any]]]:
        """Export the data of the class, as a dict of the attributes.

        Other ExportableMixin classes are exported as dicts.

        The exported data should be able to re-create a copy of the class
            that is identical to the class the data was exported from.
        """
        return {
            key: value.export() if hasattr(value, "export") else value
            for key, value in self.__dict__.copy().items()
        }
