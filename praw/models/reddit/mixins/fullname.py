"""Provide the FullnameMixin class."""


class FullnameMixin:
    """Interface for classes that have a fullname."""

    _kind = None

    @property
    def fullname(self) -> str:
        """Return the object's fullname.

        A fullname is an object's kind mapping like ``t3`` followed by an
        underscore and the object's base36 ID, e.g., ``t1_c5s96e0``.

        """
        return "{}_{}".format(self._kind, self.id)
