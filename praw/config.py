"""Provides the code to load PRAW's configuration file `praw.ini`."""
import configparser
import os
import sys
from threading import Lock
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union
from warnings import warn

from .exceptions import ClientException

_T = TypeVar("_T")


class _NotSet:
    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __str__(self):
        return "NotSet"


class Config:
    """A class containing the configuration for a reddit site."""

    CONFIG = None
    CONFIG_NOT_SET = _NotSet()  # Represents a config value that is not set.
    LOCK = Lock()
    INTERPOLATION_LEVEL = {
        "basic": configparser.BasicInterpolation,
        "extended": configparser.ExtendedInterpolation,
    }

    @property
    def custom(self) -> Dict[str, Any]:
        warn(
            "Using the custom attribute is deprecated, and will be removed "
            "from PRAW 8.0.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return dict(**self.file_settings, **self.code_settings)

    @staticmethod
    def _config_boolean(item):
        if isinstance(item, bool):
            return item
        return item.lower() in {"1", "yes", "true", "on"}

    @classmethod
    def _load_config(cls, config_interpolation: Optional[str] = None):
        """Attempt to load settings from various praw.ini files."""
        if config_interpolation is not None:
            interpolator_class = cls.INTERPOLATION_LEVEL[
                config_interpolation
            ]()
        else:
            interpolator_class = None
        config = configparser.ConfigParser(interpolation=interpolator_class)
        module_dir = os.path.dirname(sys.modules[__name__].__file__)
        if "APPDATA" in os.environ:  # Windows
            os_config_path = os.environ["APPDATA"]
        elif "XDG_CONFIG_HOME" in os.environ:  # Modern Linux
            os_config_path = os.environ["XDG_CONFIG_HOME"]
        elif "HOME" in os.environ:  # Legacy Linux
            os_config_path = os.path.join(os.environ["HOME"], ".config")
        else:
            os_config_path = None
        locations = [os.path.join(module_dir, "praw.ini"), "praw.ini"]
        if os_config_path is not None:
            locations.insert(1, os.path.join(os_config_path, "praw.ini"))
        config.read(locations)
        cls.CONFIG = config

    @property
    def short_url(self) -> str:
        """Return the short url or raise a ClientException when not set."""
        if self._short_url is self.CONFIG_NOT_SET:
            raise ClientException("No short domain specified.")
        return self._short_url

    def __init__(
        self,
        site_name: str,
        config_interpolation: Optional[str] = None,
        **settings: Any
    ):
        """Initialize a Config instance."""
        with Config.LOCK:
            if Config.CONFIG is None:
                self._load_config(config_interpolation)

        self._settings = settings
        self.file_settings = Config.CONFIG.items(site_name)
        self.code_settings = settings

        self.client_id = self.client_secret = self.oauth_url = None
        self.reddit_url = self.refresh_token = self.redirect_uri = None
        self.password = self.user_agent = self.username = None

        self._initialize_attributes()

    def _fetch(self, key):
        value = self.custom[key]
        del self.custom[key]
        return value

    def _fetch_default(self, key, default=None):
        if key not in self.custom:
            return default
        return self._fetch(key)

    def _fetch_or_not_set(self, key):
        if key in self._settings:  # Passed in values have the highest priority
            return self._fetch(key)

        env_value = os.getenv("praw_{}".format(key))
        ini_value = self._fetch_default(key)  # Needed to remove from custom

        # Environment variables have higher priority than praw.ini settings
        return env_value or ini_value or self.CONFIG_NOT_SET

    def fetch_attribute(
        self,
        key,
        convert_to_type: Optional[Union[Type[_T], Callable[[Any], _T]]] = None,
        default: Union[_NotSet, Any] = CONFIG_NOT_SET,
        environment_variable: bool = True,
        required: bool = False,
    ) -> Union[str, _T]:
        """Fetch an attribute from the config.

        Config hierarchy from lowest to highest:

        1. ``praw.ini`` file
        2. Environment variables
        3. Hardcoded values

        The highest priority is given to values that are passed as keyword
        arguments into the Config class, and by extension, the Reddit class.

        Environment variables have the second highest priority. Only
        environment variables that start with ``praw_`` followed by the
        attribute name will be looked at.

        The lowest priority goes to values in a ``praw.ini`` file.

        :param key: The key that you are trying to get the value of
        :param convert_to_type: A class or other callable that returns an
            instance of a type. If specified, the value will be converted to
            the specified type, and an instance of that type will be returned.
            If the type conversion returns an error, an instance of
            :py:class:`ValueError` will be thrown. (Default: None)

            .. note:: If a value is provided, it should only take one
                positional argument, which will be the value of the key.

        :param default: If no value is found for the key, then the default will
            be returned. By default, the Config's ``NotSet`` instance will be
            returned. In this way, it is possible to check if a key is set or
            not, by checking for equality with ``Config.CONFIG_NOT_SET``.

            .. note:: The default value will be converted to the type specified
                in parameter ``convert_to_type``, so it is recommended to
                either set a default value that can be converted (such as an
                empty string ``""``), or to set the parameter ``required`` to
                True.

        :param environment_variable: If set to True, then environment variables
            will be used as a source of the value. If set to False, then the
            only sources of values will be parameters passed into the config
            class and the ``praw.ini`` file. (Default: True)
        :param required: If set to True, if a value is not found, an instance
            of :py:class:`KeyError` will be raised, instead of returning the
            default value. (Default: False)
        :returns: An instance of ``convert_to_type`` if specified, else returns
            a string.

        For example, to fetch the value of key ``"subreddit"``, and convert the
        value into an instance of :class:`.Subreddit`, while supplying a
        default value of ``"test"``:

        .. code-block:: python

            subreddit = reddit.config.fetch_attribute("subreddit",
                        convert_to_type=reddit.subreddit,
                        default="test")

        This code will first check if the Config instance, and by extension,
        the Reddit instance, was provided a keyword argument containing the
        key name and a value, such as the code below:

        .. code-block:: python

            reddit = Reddit(client_id="...",
                            client_secret="...",
                            subreddit="redditdev",
                            user_agent="Subreddit Scraper Bot")

        This would use the value ``"redditdev"``, and since the code earlier
        also provided parameter ``convert_to_type`` with a value of
        ``reddit.subreddit``, the return value will be the callable given the
        value as the only parameter. Therefore, the return value will be

        .. code-block:: python

            subreddit = reddit.subreddit("redditdev")

        The final value of ``subreddit`` will be an instance of
        :class:`.Subreddit` with a display_name of ``"redditdev"``.
        """
        return_value = default
        ini_value = self.file_settings.get(key)
        if ini_value is not None:
            return_value = ini_value
        if environment_variable:
            env_value = os.getenv("praw_{}".format(key))
            if env_value is not None:
                return_value = env_value
        code_value = self.code_settings.get(key)
        if code_value is not None:
            return_value = code_value
        if required and return_value == default:
            message = (
                "Required key {key} not found. Please provide the value in "
                'the Reddit() call, such as ``Reddit({key}="value")`` or as '
                'a line in the praw.ini file, such as ``{key}="value"``.'
            )
            if environment_variable:
                message += (
                    " In addition, you can specify the value as an "
                    "environment variable, by running ``export praw_"
                    '{key}="value"`` on a Unix system (Mac OS X and '
                    "Linux systems), by running ``setx praw_{key} "
                    '"value"`` on Windows Command Prompt (cmd.exe), or '
                    'by running ``$Env:praw_{key}= "value"`` on Windows'
                    " Powershell."
                )
            raise KeyError(message.format(key=key))
        if convert_to_type is not None:
            try:
                return convert_to_type(return_value)
            except Exception as exc:
                raise ValueError(
                    "The value {!r} (type {}) of key {} could not be converted"
                    " to the requested type. Please ensure that the callable "
                    "takes one positional parameter only, and that the value "
                    "can be converted to the requested type.".format(
                        return_value, type(return_value).__name__, key
                    )
                ) from exc
        return return_value

    def _initialize_attributes(self):
        self._short_url = (
            self._fetch_default("short_url") or self.CONFIG_NOT_SET
        )
        self.check_for_updates = self._config_boolean(
            self._fetch_or_not_set("check_for_updates")
        )
        self.kinds = {
            x: self._fetch("{}_kind".format(x))
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
                raise ValueError(
                    "An incorrect config type was given for option {}. The "
                    "expected type is {}, but the given value is {}.".format(
                        attribute,
                        conversion.__name__,
                        getattr(self, attribute),
                    )
                )
