from typing import List

from .base import BaseList as BaseList
from ..reddit.redditor import Redditor


class RedditorList(BaseList, List[Redditor]):
    CHILD_ATTRIBUTE: str = ...
