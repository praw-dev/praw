from .base import PRAWBase as PRAWBase
from typing import Any

class ModAction(PRAWBase):
    @property
    def mod(self): ...
    @mod.setter
    def mod(self, value: Any) -> None: ...
