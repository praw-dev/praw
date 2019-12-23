from typing import Any

from .base import PRAWBase as PRAWBase


class ModAction(PRAWBase):
    @property
    def mod(self): ...
    @mod.setter
    def mod(self, value: Any) -> None: ...
