from typing import Any, NoReturn

from .base import PRAWBase as PRAWBase
from .reddit.redditor import Redditor


class ModAction(PRAWBase):
    @property
    def mod(self) -> Redditor: ...
    @mod.setter
    def mod(self, value: Any) -> NoReturn: ...
