"""This file should be updated as files/classes/functions are deprecated."""

import pytest
from . import UnitTest
import warnings


class TestDeprecation(UnitTest):
    def test_deprecation_modaction(self):
        warnings.filterwarnings("error", category=DeprecationWarning)
        with pytest.raises(DeprecationWarning):
            import praw.models.modaction  # noqa
        warnings.filterwarnings("default", category=DeprecationWarning)
