"""PRAW Integration test suite."""
import os
from urllib.parse import quote_plus

import betamax
import pytest
import requests
from betamax.cassette import Cassette

from praw import Reddit

from .utils import (
    PrettyJSONSerializer,
    ensure_environment_variables,
    ensure_integration_test,
    filter_access_token,
)

CASSETTES_PATH = "tests/integration/cassettes"
existing_cassettes = set()
used_cassettes = set()


class IntegrationTest:
    """Base class for PRAW integration tests."""

    @pytest.fixture(autouse=True)
    def cassette(self, request, recorder, cassette_name):
        """Wrap a test in a VCR.py cassette"""
        global used_cassettes
        kwargs = {}
        for marker in request.node.iter_markers("recorder_kwargs"):
            if marker is not None:
                append_placeholders = marker.kwargs.pop("append_placeholders", None)
                if append_placeholders is not None:
                    recorder.config.default_cassette_options["placeholders"].append(
                        append_placeholders
                    )
                for key, value in marker.kwargs.items():
                    #  Don't overwrite existing values since function markers are
                    #  provided before class markers.
                    kwargs.setdefault(key, value)
        with recorder.use_cassette(cassette_name, **kwargs) as recorder:
            cassette = recorder.current_cassette
            if cassette.is_recording():
                ensure_environment_variables()
            yield recorder
            ensure_integration_test(cassette)
            used_cassettes.add(cassette_name)

    @pytest.fixture(autouse=True)
    def read_only(self, reddit):
        """Make reddit instance read-only."""
        # Require tests to explicitly disable read_only mode.
        reddit.read_only = True

    @pytest.fixture(autouse=True)
    def recorder(self):
        """Configure VCR instance."""
        session = requests.Session()
        recorder = betamax.Betamax(session)
        recorder.register_serializer(PrettyJSONSerializer)
        with betamax.Betamax.configure() as config:
            config.cassette_library_dir = "tests/integration/cassettes"
            config.default_cassette_options["serialize_with"] = "prettyjson"
            config.before_record(callback=filter_access_token)
            for key, value in pytest.placeholders.__dict__.items():
                if key == "password":
                    value = quote_plus(value)
                config.define_cassette_placeholder(f"<{key.upper()}>", value)
            yield recorder
            # since placeholders persist between tests
            Cassette.default_cassette_options["placeholders"] = []

    @pytest.fixture(scope="session")
    def cassette_tracker(self):
        """Return a dictionary to track cassettes."""
        global existing_cassettes
        for cassette in os.listdir(CASSETTES_PATH):
            if cassette.endswith(".json"):
                existing_cassettes.add(cassette.replace(".json", ""))
        yield
        unused_cassettes = existing_cassettes - used_cassettes
        if unused_cassettes and os.getenv("ENSURE_NO_UNUSED_CASSETTES", "0") == "1":
            raise AssertionError(
                f"The following cassettes are unused: {', '.join(unused_cassettes)}."
            )

    @pytest.fixture
    def cassette_name(self, request):
        """Return the name of the cassette to use."""
        marker = request.node.get_closest_marker("cassette_name")
        if marker is None:
            return (
                f"{request.cls.__name__}.{request.node.name}"
                if request.cls
                else request.node.name
            )
        return marker.args[0]

    @pytest.fixture
    def reddit(self, recorder):
        """Configure Reddit."""
        session = recorder.session
        session.headers["Accept-Encoding"] = "identity"
        reddit_kwargs = {
            "client_id": pytest.placeholders.client_id,
            "client_secret": pytest.placeholders.client_secret,
            "requestor_kwargs": {"session": session},
            "user_agent": pytest.placeholders.user_agent,
        }

        if pytest.placeholders.refresh_token != "placeholder_refresh_token":
            reddit_kwargs["refresh_token"] = pytest.placeholders.refresh_token
        else:
            reddit_kwargs["username"] = pytest.placeholders.username
            reddit_kwargs["password"] = pytest.placeholders.password

        with Reddit(**reddit_kwargs) as reddit:
            yield reddit
