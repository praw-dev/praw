"""Compatibility module."""

import sys

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

string_types = (str,)  # pylint: disable=invalid-name
if PY2:
    # pylint: disable=invalid-name,undefined-variable
    string_types = (basestring,)  # noqa: F821

# pylint: disable=import-error,no-name-in-module,unused-import
if PY2:
    import ConfigParser as configparser  # noqa: F401
    from urlparse import urljoin, urlparse  # noqa: F401
else:
    import configparser  # noqa: F401
    from urllib.parse import urljoin, urlparse  # noqa: F401
