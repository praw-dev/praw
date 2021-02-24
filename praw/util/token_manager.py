"""Token Manager classes.

There should be a 1-to-1 mapping betwen an instance of a subclass of
:class:`.BaseTokenManager` and a :class:`.Reddit` instance.

A few trivial token manager classes are provided here, but it is expected that
PRAW users will create their own token manager classes suitable for their needs.

See ref:`using_refresh_tokens` for examples on how to leverage these classes.

"""


class BaseTokenManager:
    """An abstract class for all token managers."""

    def __init__(self):
        """Prepare attributes needed by all token manager classes."""
        self._reddit = None

    @property
    def reddit(self):
        """Return the :class:`.Reddit` instance bound to the token manager."""
        return self._reddit

    @reddit.setter
    def reddit(self, value):
        if self._reddit is not None:
            raise RuntimeError(
                "``reddit`` can only be set once and is done automatically"
            )
        self._reddit = value

    def post_refresh_callback(self, authorizer):
        """Handle callback that is invoked after a refresh token is used.

        :param authorizer: The ``prawcore.Authorizer`` instance used containing
            ``access_token`` and ``refresh_token`` attributes.

        This function will be called after refreshing the access and refresh
        tokens. This callback can be used for saving the updated
        ``refresh_token``.

        """
        raise NotImplementedError("``post_refresh_callback`` must be extended.")

    def pre_refresh_callback(self, authorizer):
        """Handle callback that is invoked before refreshing PRAW's authorization.

        :param authorizer: The ``prawcore.Authorizer`` instance used containing
            ``access_token`` and ``refresh_token`` attributes.

        This callback can be used to inspect and modify the attributes of the
        ``prawcore.Authorizer`` instance, such as setting the
        ``refresh_token``.

        """
        raise NotImplementedError("``pre_refresh_callback`` must be extended.")


class FileTokenManager(BaseTokenManager):
    """Provides a trivial single-file based token manager."""

    def __init__(self, filename):
        """Load and save refresh tokens from a file.

        :param filename: The file the contains the refresh token.

        """
        super().__init__()
        self._filename = filename

    def post_refresh_callback(self, authorizer):
        """Update the saved copy of the refresh token."""
        with open(self._filename, "w") as fp:
            fp.write(authorizer.refresh_token)

    def pre_refresh_callback(self, authorizer):
        """Load the refresh token from the file."""
        if authorizer.refresh_token is None:
            with open(self._filename) as fp:
                authorizer.refresh_token = fp.read().strip()
