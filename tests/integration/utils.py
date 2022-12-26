"""Pytest utils for integration tests."""

import json

import betamax
import pytest
from betamax.serializers import JSONSerializer


def ensure_environment_variables():
    """Ensure needed environment variables for recording a new cassette are set."""
    for key in (
        "client_id",
        "client_secret",
    ):
        if getattr(pytest.placeholders, key) == f"placeholder_{key}":
            raise ValueError(
                f"Environment variable 'prawtest_{key}' must be set for recording new"
                " cassettes."
            )
    auth_set = False
    for auth_keys in [["refresh_token"], ["username", "password"]]:
        if all(
            getattr(pytest.placeholders, key) != f"placeholder_{key}"
            for key in auth_keys
        ):
            auth_set = True
            break
    if not auth_set:
        raise ValueError(
            "Environment variables 'prawtest_refresh_token' or 'prawtest_username' and"
            " 'prawtest_password' must be set for new cassette recording."
        )


def ensure_integration_test(cassette):
    if cassette.is_recording():
        is_integration_test = not cassette.is_empty()
        action = "record"
    else:
        is_integration_test = any(
            [interaction.used for interaction in cassette.interactions]
        )
        action = "play back"
    message = f"Cassette did not {action} any requests. This test can be a unit test."
    assert is_integration_test, message


def filter_access_token(interaction, current_cassette):
    """Add Betamax placeholder to filter access token."""
    request_uri = interaction.data["request"]["uri"]
    response = interaction.data["response"]
    if "api/v1/access_token" not in request_uri or response["status"]["code"] != 200:
        return
    body = response["body"]["string"]
    try:
        token = json.loads(body)["access_token"]
    except (KeyError, TypeError, ValueError):
        return
    current_cassette.placeholders.append(
        betamax.cassette.cassette.Placeholder(
            placeholder="<ACCESS_TOKEN>", replace=token
        )
    )


class PrettyJSONSerializer(JSONSerializer):
    name = "prettyjson"

    def serialize(self, cassette_data):
        return f"{json.dumps(cassette_data, sort_keys=True, indent=2, separators=(',', ': '))}\n"
