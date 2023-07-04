import sys
from datetime import datetime

# Do not touch these. They use the local PRAW over the global PRAW.
sys.path.insert(0, ".")
sys.path.insert(1, "..")

from praw import __version__  # noqa: E402

copyright = datetime.today().strftime("%Y, Bryce Boe")
exclude_patterns = ["_build"]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]
html_theme = "furo"
htmlhelp_basename = "PRAW"
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
master_doc = "index"
nitpick_ignore = [
    ("py:class", "IO"),
    ("py:class", "prawcore.requestor.Requestor"),
    ("py:class", "praw.models.redditors.PartialRedditor"),
]
nitpicky = True
project = "PRAW"
pygments_style = "sphinx"
release = __version__
source_suffix = ".rst"
suppress_warnings = ["image.nonlocal_uri"]
version = ".".join(__version__.split(".", 2)[:2])


def skip(app, what, name, obj, skip, options):
    if name in {
        "__call__",
        "__contains__",
        "__getitem__",
        "__init__",
        "__iter__",
        "__len__",
    }:
        return False
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
