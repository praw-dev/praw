"""Defaults for :func:`~.validate_types`, such as :func:`~.validate_id`."""

from . import validate_types, _remove_extra_attrs


def validate_id(id_data, *_args, ignore_none=True, **parent_kwargs):
    """Check variable data with an assumed name of 'id'.

    :param id_data: The value of the variable with name 'id'

    :param ignore_none: (Inherited from :func:`~.validate_types`) Toggles
        allowing the value of 'id' to be None (default True)

    This function is just a fancy wrapper for :func:`~.validate_types` and
        supports all of the same arguments as :func:`~.validate_types`.

    """
    parent_kwargs = _remove_extra_attrs(parent_kwargs)
    return validate_types(
        id_data,
        str,
        variable_name="id",
        ignore_none=ignore_none,
        **parent_kwargs
    )


def validate_url(url_data, *_args, ignore_none=True, **parent_kwargs):
    """Check variable data with an assumed name of 'url'.

    :param url_data: The value of the variable with name 'url'

    :param ignore_none: (Inherited from :func:`~.validate_types`) Toggles
        allowing the value of 'url' to be None (default True)

    This function is just a fancy wrapper for :func:`~.validate_types` and
        supports all of the same arguments as :func:`~.validate_types`

    """
    parent_kwargs = _remove_extra_attrs(parent_kwargs)
    return validate_types(
        url_data,
        str,
        variable_name="url",
        ignore_none=ignore_none,
        **parent_kwargs
    )
