from typing import Dict, Union, NoReturn

from ..reddit import Reddit


class Preferences:
    def __call__(self) -> Dict[str, Union[str, bool]]: ...
    def __init__(self, reddit: Reddit) -> NoReturn: ...
    def update(self, **preferences: Union[str, bool]): ...