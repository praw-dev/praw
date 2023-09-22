"""Test praw.models.redditors."""

from unittest import mock

from .. import UnitTest


class TestRedditors(UnitTest):
    def test_partial_redditors(self, reddit):
        with mock.patch.object(reddit, "request") as mock_method:
            in_ids_list = [f"t2_{int(n)}" for n in range(100)]
            list(reddit.redditors.partial_redditors(in_ids_list))

            assert mock_method.call_count == 1
            assert mock_method.call_args[1]["params"]["ids"] == ",".join(in_ids_list)

        with mock.patch.object(reddit, "request") as mock_method:
            in_ids_list = [f"t2_{int(n)}" for n in range(102)]
            list(reddit.redditors.partial_redditors(in_ids_list))

            assert mock_method.call_count == 2
            cal = mock_method.call_args_list
            assert cal[0][1]["params"]["ids"] == ",".join(in_ids_list[:100])
            assert cal[1][1]["params"]["ids"] == ",".join(in_ids_list[-2:])

    def test_partial_redditors__no_typeerror(self, reddit):
        func = reddit.redditors.partial_redditors
        with mock.patch.object(reddit, "request"):
            func(list("abc"))
            func(tuple("abc"))
            func(c for c in "abc")

    def test_search__params_not_modified(self, reddit):
        params = {"dummy": "value"}
        generator = reddit.redditors.search(None, params=params)
        assert generator.params["dummy"] == "value"
        assert params == {"dummy": "value"}
