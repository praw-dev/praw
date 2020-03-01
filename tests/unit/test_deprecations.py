"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from . import UnitTest


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecation(UnitTest):
    def test_validate_on_submit(self):
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit
        self.reddit.validate_on_submit = True
        assert self.reddit.validate_on_submit
        self.reddit.validate_on_submit = False
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit
