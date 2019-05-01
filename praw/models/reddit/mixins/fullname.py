"""Provide the FullnameMixin class."""
from ....const import API_PATH
from ....exceptions import PRAWException


class FullnameMixin(object):
    """Interface for classes that have a fullname."""

    @property
    def fullname(self):
        """Return the object's fullname.

        A fullname is an object's kind mapping like ``t3`` followed by an
        underscore and the object's base36 ID, e.g., ``t1_c5s96e0``.

        """
        return "{}_{}".format(
            self._reddit._objector.kind(self), self.id
        )  # pylint: disable=invalid-name

    def _fetch(self):
        if "_info_path" in dir(self):
            super(FullnameMixin, self)._fetch()
        else:
            self._info_params["id"] = self.fullname
            children = self._reddit.get(
                API_PATH["info"], params=self._info_params
            ).children
            if not children:
                raise PRAWException(
                    "No {!r} data returned for thing {}".format(
                        self.__class__.__name__, self.fullname
                    )
                )
            other = children[0]
            self.__dict__.update(other.__dict__)
            self._fetched = True
