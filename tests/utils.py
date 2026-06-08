"""Pytest utils for integration tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from vcr.persisters.filesystem import CassetteNotFoundError, FilesystemPersister
from vcr.serialize import deserialize, serialize

from tests.conftest import cassette_placeholders as _placeholders


def ensure_environment_variables():
    """Ensure needed environment variables for recording a new cassette are set."""
    for key in (
        "client_id",
        "client_secret",
    ):
        if getattr(pytest.placeholders, key) == f"placeholder_{key}":
            msg = f"Environment variable 'prawtest_{key}' must be set for recording new cassettes."
            raise ValueError(msg)
    auth_set = False
    for auth_keys in [["refresh_token"], ["username", "password"]]:
        if all(getattr(pytest.placeholders, key) != f"placeholder_{key}" for key in auth_keys):
            auth_set = True
            break
    if not auth_set:
        msg = (
            "Environment variables 'prawtest_refresh_token' or 'prawtest_username' and"
            " 'prawtest_password' must be set for new cassette recording."
        )
        raise ValueError(msg)


def ensure_integration_test(cassette):
    """Ensure test being run is actually an integration test and error if not."""
    if cassette.write_protected:
        is_integration_test = cassette.play_count > 0
        action = "play back"
    else:  # pragma: no cover
        is_integration_test = cassette.dirty
        action = "record"
    message = f"Cassette did not {action} any requests. This test can be a unit test."
    assert is_integration_test, message


def filter_access_token(response):  # pragma: no cover
    """Add VCR callback to filter access token."""
    if response["status"]["code"] != 200:
        return response
    # ``before_record_response`` only receives the response, so the access token is
    # located by inspecting the body rather than the request URI.
    body = response["body"]["string"]
    try:
        token = json.loads(body.decode())["access_token"]
    except (AttributeError, KeyError, TypeError, ValueError):
        return response
    response["body"]["string"] = body.replace(token.encode("utf-8"), b"<ACCESS_TOKEN>")
    _placeholders["access_token"] = token
    return response


class CustomPersister(FilesystemPersister):
    """Custom persister to handle placeholders."""

    additional_placeholders = {}

    @classmethod
    def add_additional_placeholders(cls, placeholders: dict[str, str]):
        """Add additional placeholders."""
        cls.additional_placeholders.update(placeholders)

    @classmethod
    def clear_additional_placeholders(cls):
        """Clear additional placeholders."""
        cls.additional_placeholders = {}

    @classmethod
    def load_cassette(cls, cassette_path, serializer):
        """Load cassette."""
        try:
            with Path(cassette_path).open() as f:
                cassette_content = f.read()
        except OSError as error:  # pragma: no cover
            msg = "Cassette not found."
            raise CassetteNotFoundError(msg) from error
        for replacement, value in [
            (v, f"<{k.upper()}>") for k, v in {**cls.additional_placeholders, **_placeholders}.items()
        ]:
            cassette_content = cassette_content.replace(value, replacement)
        return deserialize(cassette_content, serializer)

    @classmethod
    def save_cassette(cls, cassette_path, cassette_dict, serializer):  # pragma: no cover
        """Save cassette."""
        cassette_path = Path(cassette_path)
        data = serialize(cassette_dict, serializer)
        for replacement, value in [
            (f"<{k.upper()}>", v) for k, v in {**cls.additional_placeholders, **_placeholders}.items()
        ]:
            data = data.replace(value, replacement)
        dirname = cassette_path.parent
        if dirname and not dirname.exists():
            dirname.mkdir(parents=True)
        with cassette_path.open("w") as f:
            f.write(data)


class CustomSerializer:
    """Custom serializer to maintain the pretty JSON cassette format."""

    @staticmethod
    def deserialize(cassette_string):
        """Deserialize cassette."""
        return json.loads(cassette_string)

    @classmethod
    def serialize(cls, cassette_dict):  # pragma: no cover
        """Serialize cassette."""
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        try:
            i = timestamp.rindex(".")
        except ValueError:
            pass
        else:
            timestamp = timestamp[:i]
        cassette_dict["recorded_at"] = timestamp
        return f"{json.dumps(cassette_dict, indent=2, sort_keys=True)}\n"
