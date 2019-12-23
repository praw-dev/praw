from typing import List

from .base import PRAWBase as PRAWBase


class Stylesheet(PRAWBase):
    images: List[str]
    stylesheet: str