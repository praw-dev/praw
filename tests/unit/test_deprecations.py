"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from . import UnitTest


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecation(UnitTest):
    pass  # No current deprecations
