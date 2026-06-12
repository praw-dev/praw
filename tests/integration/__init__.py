"""PRAW Integration test suite."""

import os
from pathlib import Path

import pytest
from vcr import VCR

from praw import Reddit

from ..utils import (
    CustomPersister,
    CustomSerializer,
    ensure_environment_variables,
    ensure_integration_test,
    filter_access_token,
)

CASSETTES_PATH = Path("tests/integration/cassettes")
existing_cassettes = set()
used_cassettes = set()

# VCR's ``uri`` matcher compares the full URI as a string, which is sensitive to query
# parameter order. Betamax compared query parameters order-independently, so expand
# ``uri`` into components that use VCR's order-independent ``query`` matcher.
URI_MATCHERS = ["scheme", "host", "port", "path", "query"]


class IntegrationTest:
    """Base class for PRAW integration tests."""

    @pytest.fixture(autouse=True, scope="session")
    def cassette_tracker(self):
        """Track cassettes to ensure unused cassettes are not uploaded."""
        existing_cassettes.update(cassette.name[: cassette.name.rindex(".")] for cassette in CASSETTES_PATH.iterdir())
        yield
        unused_cassettes = existing_cassettes - used_cassettes
        if unused_cassettes and os.getenv("ENSURE_NO_UNUSED_CASSETTES", "0") == "1":
            msg = f"The following cassettes are unused: {', '.join(unused_cassettes)}."
            raise AssertionError(msg)

    @pytest.fixture(autouse=True)
    def cassette(self, request, recorder, cassette_name):
        """Wrap a test in a VCR cassette."""
        kwargs = {}
        for marker in request.node.iter_markers("add_placeholder"):
            CustomPersister.add_additional_placeholders(marker.kwargs)
        for marker in request.node.iter_markers("recorder_kwargs"):
            for key, value in marker.kwargs.items():
                #  Don't overwrite existing values since function markers are provided
                #  before class markers.
                kwargs.setdefault(key, value)
        if "match_on" in kwargs:
            kwargs["match_on"] = _expand_uri_matcher(kwargs["match_on"])
        with recorder.use_cassette(cassette_name, **kwargs) as _cassette:
            if not _cassette.write_protected:  # pragma: no cover
                ensure_environment_variables()
            yield _cassette
            ensure_integration_test(_cassette)
            used_cassettes.add(cassette_name)

    @pytest.fixture(autouse=True)
    def read_only(self, reddit):
        """Make the Reddit instance read-only."""
        # Require tests to explicitly disable read_only mode.
        reddit.read_only = True

    @pytest.fixture(autouse=True)
    def recorder(self):
        """Configure VCR."""
        vcr = VCR()
        vcr.before_record_response = filter_access_token
        vcr.cassette_library_dir = str(CASSETTES_PATH)
        vcr.decode_compressed_response = True
        vcr.match_on = ["method", *URI_MATCHERS]
        vcr.path_transformer = VCR.ensure_suffix(".json")
        vcr.register_persister(CustomPersister)
        vcr.register_serializer("custom_serializer", CustomSerializer)
        vcr.serializer = "custom_serializer"
        yield vcr
        CustomPersister.clear_additional_placeholders()

    @pytest.fixture
    def cassette_name(self, request):
        """Return the name of the cassette to use."""
        marker = request.node.get_closest_marker("cassette_name")
        if marker is None:
            return f"{request.cls.__name__}.{request.node.name}" if request.cls else request.node.name
        return marker.args[0]

    @pytest.fixture
    def reddit(self):
        """Configure Reddit."""
        reddit_kwargs = {
            "client_id": pytest.placeholders.client_id,
            "client_secret": pytest.placeholders.client_secret,
            "user_agent": pytest.placeholders.user_agent,
        }

        if pytest.placeholders.refresh_token != "placeholder_refresh_token":
            reddit_kwargs["refresh_token"] = pytest.placeholders.refresh_token
        else:
            reddit_kwargs["username"] = pytest.placeholders.username
            reddit_kwargs["password"] = pytest.placeholders.password

        with Reddit(**reddit_kwargs) as reddit:
            yield reddit


def _expand_uri_matcher(matchers):
    """Replace the ``uri`` matcher with order-independent component matchers."""
    expanded = []
    for matcher in matchers:
        expanded.extend(URI_MATCHERS if matcher == "uri" else [matcher])
    return expanded
