"""Provide the Auth class."""

from __future__ import annotations

from prawcore import (
    Authorizer,
    DeviceIDAuthorizer,
    ImplicitAuthorizer,
    UntrustedAuthenticator,
    session,
)

from praw.exceptions import InvalidImplicitAuth, MissingRequiredAttributeException
from praw.models.base import PRAWBase


class Auth(PRAWBase):
    """Auth provides an interface to Reddit's authorization."""

    @property
    def limits(self) -> dict[str, str | int | None]:
        """Return a dictionary containing the rate limit info.

        The keys are:

        :remaining: The number of requests remaining to be made in the current rate
            limit window.
        :used: The number of requests made in the current rate limit window.

        All values are initially ``None`` as these values are set in response to issued
        requests.

        """
        assert self._reddit._core is not None
        data = self._reddit._core.rate_limiter
        return {
            "remaining": data.remaining,
            "used": data.used,
        }

    def authorize(self, code: str) -> str | None:
        """Complete the web authorization flow and return the refresh token.

        :param code: The code obtained through the request to the redirect uri.

        :returns: The obtained refresh token, if available, otherwise ``None``.

        The session's active authorization will be updated upon success.

        """
        assert self._reddit._read_only_core is not None
        authenticator = self._reddit._read_only_core.authorizer.authenticator
        authorizer = Authorizer(authenticator=authenticator)
        authorizer.authorize(code)
        authorized_session = session(authorizer=authorizer, window_size=self._reddit.config.window_size)
        self._reddit._core = self._reddit._authorized_core = authorized_session
        return authorizer.refresh_token

    def implicit(self, *, access_token: str, expires_in: int, scope: str) -> None:
        """Set the active authorization to be an implicit authorization.

        :param access_token: The access_token obtained from Reddit's callback.
        :param expires_in: The number of seconds the ``access_token`` is valid for. The
            origin of this value was returned from Reddit's callback. You may need to
            subtract an offset before passing in this number to account for a delay
            between when Reddit prepared the response, and when you make this function
            call.
        :param scope: A space-delimited string of Reddit OAuth2 scope names as returned
            from Reddit's callback.

        :raises: :class:`.InvalidImplicitAuth` if :class:`.Reddit` was initialized for a
            non-installed application type.

        """
        assert self._reddit._read_only_core is not None
        authenticator = self._reddit._read_only_core.authorizer.authenticator
        if not isinstance(authenticator, UntrustedAuthenticator):
            raise InvalidImplicitAuth
        implicit_session = session(
            authorizer=ImplicitAuthorizer(
                access_token=access_token, authenticator=authenticator, expires_in=expires_in, scope=scope
            ),
            window_size=self._reddit.config.window_size,
        )
        self._reddit._core = self._reddit._authorized_core = implicit_session

    def scopes(self) -> set[str]:
        """Return a set of scopes included in the current authorization.

        For read-only authorizations this should return ``{"*"}``.

        """
        assert self._reddit._core is not None
        authorizer = self._reddit._core.authorizer
        if not authorizer.is_valid():
            # The active core authorizer is always refreshable here; ImplicitAuthorizer
            # is the only BaseAuthorizer without refresh() and never reaches this path.
            assert isinstance(authorizer, (Authorizer, DeviceIDAuthorizer))
            authorizer.refresh()
        assert authorizer.scopes is not None
        return authorizer.scopes

    def url(
        self,
        *,
        duration: str = "permanent",
        implicit: bool = False,
        scopes: list[str],
        state: str,
    ) -> str:
        """Return the URL used out-of-band to grant access to your application.

        :param duration: Either ``"permanent"`` or ``"temporary"`` (default:
            ``"permanent"``). ``"temporary"`` authorizations generate access tokens that
            last only 1 hour. ``"permanent"`` authorizations additionally generate a
            refresh token that expires 1 year after the last use and can be used
            indefinitely to generate new hour-long access tokens. This value is ignored
            when ``implicit=True``.
        :param implicit: For **installed** applications, this value can be set to use
            the implicit, rather than the code flow. When ``True``, the ``duration``
            argument has no effect as only temporary tokens can be retrieved.
        :param scopes: A list of OAuth scopes to request authorization for.
        :param state: A string that will be reflected in the callback to
            ``redirect_uri``. This value should be temporarily unique to the client for
            whom the URL was generated for.

        """
        assert self._reddit._read_only_core is not None
        assert self._reddit._read_only_core._authorizer is not None
        authenticator = self._reddit._read_only_core._authorizer._authenticator
        if authenticator.redirect_uri is self._reddit.config.CONFIG_NOT_SET:
            msg = "redirect_uri must be provided"
            raise MissingRequiredAttributeException(msg)
        if isinstance(authenticator, UntrustedAuthenticator):
            return authenticator.authorize_url(
                duration="temporary" if implicit else duration,
                implicit=implicit,
                scopes=scopes,
                state=state,
            )
        if implicit:
            raise InvalidImplicitAuth
        return authenticator.authorize_url(duration=duration, scopes=scopes, state=state)
