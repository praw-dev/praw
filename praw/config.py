"""Provides the code to load PRAW's configuration file ``praw.ini``."""

from __future__ import annotations

import configparser
import os
from importlib.resources import files
from pathlib import Path
from threading import Lock
from types import MappingProxyType
from typing import Any
from warnings import warn

from praw.exceptions import ClientException


class _NotSet:
    def __bool__(self) -> bool:
        return False

    __nonzero__ = __bool__

    def __str__(self) -> str:
        return "NotSet"


class Config:
    """A class containing the configuration for a Reddit site."""

    CONFIG: configparser.ConfigParser | None = None
    CONFIG_NOT_SET = _NotSet()  # Represents a config value that is not set.
    INTERPOLATION_LEVEL = MappingProxyType({
        "basic": configparser.BasicInterpolation,
        "extended": configparser.ExtendedInterpolation,
    })
    LOCK = Lock()

    # Attributes populated by _initialize_attributes. client_id and user_agent are
    # validated as present by Reddit.__init__, so they are typed as required.
    client_id: str
    client_secret: str | None
    oauth_url: str
    password: str | None
    ratelimit_seconds: int
    reddit_url: str
    redirect_uri: str | None
    refresh_token: str | None
    timeout: int
    user_agent: str
    username: str | None

    @staticmethod
    def _config_boolean(*, item: bool | str | _NotSet) -> bool:
        if isinstance(item, bool):
            return item
        if isinstance(item, _NotSet):
            return False
        return item.lower() in {"1", "yes", "true", "on"}

    @staticmethod
    def _warn_on_endpoint_override(
        interpolator_class: configparser.Interpolation | None,
    ) -> None:
        """Warn if a ``praw.ini`` in the current directory overrides OAuth endpoints.

        ``praw.ini`` is loaded from the current working directory, so a file planted
        there can redirect ``oauth_url`` or ``reddit_url`` to an attacker-controlled
        host and capture credentials. Legitimate configs almost never set these keys, so
        surface a warning when they do.

        The warning can be silenced by setting the ``PRAW_ALLOW_ENDPOINT_OVERRIDE``
        environment variable. It is intentionally not a ``praw.ini`` option, as that
        would let the planted file silence its own warning.

        """
        if os.getenv("PRAW_ALLOW_ENDPOINT_OVERRIDE"):
            return
        cwd_config_path = Path("praw.ini")
        if not cwd_config_path.is_file():
            return
        cwd_config = configparser.ConfigParser(interpolation=interpolator_class)
        try:
            cwd_config.read(str(cwd_config_path))
        except configparser.Error:
            return  # A malformed file will be reported by the subsequent read.
        keys_present = set(cwd_config.defaults())
        for section in cwd_config.sections():
            keys_present.update(cwd_config.options(section))
        if overridden := sorted({"oauth_url", "reddit_url"} & keys_present):
            warn(
                f"The praw.ini in the current working directory ({cwd_config_path.resolve()})"
                f" overrides the {' and '.join(overridden)} endpoint(s). Credentials will be"
                " sent to the configured host. Remove this file or these keys if it is not"
                " trusted.",
                stacklevel=4,
            )

    @classmethod
    def _load_config(cls, *, config_interpolation: str | None = None) -> None:
        """Attempt to load settings from various praw.ini files."""
        if config_interpolation is not None:
            interpolator_class = cls.INTERPOLATION_LEVEL[config_interpolation]()
        else:
            interpolator_class = None

        config = configparser.ConfigParser(interpolation=interpolator_class)
        assert __package__ is not None
        with files(__package__).joinpath("praw.ini").open("r") as hdl:
            config.read_file(hdl)

        if "APPDATA" in os.environ:  # Windows
            os_config_path = Path(os.environ["APPDATA"])
        elif "XDG_CONFIG_HOME" in os.environ:  # Modern Linux
            os_config_path = Path(os.environ["XDG_CONFIG_HOME"])
        elif "HOME" in os.environ:  # Legacy Linux
            os_config_path = Path(os.environ["HOME"]) / ".config"
        else:
            os_config_path = None

        locations = ["praw.ini"]

        if os_config_path is not None:
            locations.insert(0, str(os_config_path / "praw.ini"))

        cls._warn_on_endpoint_override(interpolator_class)
        config.read(locations)
        cls.CONFIG = config

    @property
    def short_url(self) -> str:
        """Return the short url.

        :raises: :class:`.ClientException` if it is not set.

        """
        if isinstance(self._short_url, _NotSet):
            msg = "No short domain specified."
            raise ClientException(msg)
        return self._short_url

    def __init__(
        self,
        site_name: str,
        config_interpolation: str | None = None,
        **settings: str | bool | int | None,
    ) -> None:
        """Initialize a :class:`.Config` instance."""
        with Config.LOCK:
            if Config.CONFIG is None:
                self._load_config(config_interpolation=config_interpolation)

        self._settings = settings
        assert Config.CONFIG is not None
        self.custom = dict(Config.CONFIG.items(site_name), **settings)

        self._initialize_attributes()

    def _fetch(self, key: str) -> Any:
        value = self.custom[key]
        del self.custom[key]
        return value

    def _fetch_default(self, key: str, *, default: bool | float | str | None = None) -> Any:
        if key not in self.custom:
            return default
        return self._fetch(key)

    def _fetch_or_not_set(self, key: str) -> Any | _NotSet:
        if key in self._settings:  # Passed in values have the highest priority
            return self._fetch(key)

        env_value = os.getenv(f"praw_{key}")
        ini_value = self._fetch_default(key)  # Needed to remove from custom

        # Environment variables have higher priority than praw.ini settings
        return env_value or ini_value or self.CONFIG_NOT_SET

    def _initialize_attributes(self) -> None:
        self._short_url = self._fetch_default("short_url") or self.CONFIG_NOT_SET
        self.check_for_async = self._config_boolean(item=self._fetch_default("check_for_async", default=True))
        self.check_for_updates = self._config_boolean(item=self._fetch_or_not_set("check_for_updates"))
        self.window_size = self._fetch_default("window_size", default=600)
        self.kinds = {
            x: self._fetch(f"{x}_kind")
            for x in [
                "comment",
                "message",
                "redditor",
                "submission",
                "subreddit",
                "trophy",
            ]
        }

        for attribute in (
            "client_id",
            "client_secret",
            "redirect_uri",
            "refresh_token",
            "password",
            "user_agent",
            "username",
        ):
            setattr(self, attribute, self._fetch_or_not_set(attribute))

        for required_attribute in (
            "oauth_url",
            "ratelimit_seconds",
            "reddit_url",
            "timeout",
        ):
            setattr(self, required_attribute, self._fetch(required_attribute))

        for attribute, conversion in {
            "ratelimit_seconds": int,
            "timeout": int,
        }.items():
            try:
                setattr(self, attribute, conversion(getattr(self, attribute)))
            except ValueError:
                msg = f"An incorrect config type was given for option {attribute}. The expected type is {conversion.__name__}, but the given value is {getattr(self, attribute)}."
                raise ValueError(msg) from None
