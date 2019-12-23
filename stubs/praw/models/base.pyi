from typing import Any, Dict, NoReturn

from ..reddit import Reddit


class PRAWBase:
    @classmethod
    def parse(cls, data: Dict[Any, Any], reddit: Reddit): ...
    def __init__(self, reddit: Reddit, _data: Dict[Any, Any]) -> NoReturn: ...
