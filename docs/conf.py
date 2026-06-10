import sys
from datetime import datetime

# Do not touch these. They use the local PRAW over the global PRAW.
sys.path.insert(0, ".")
sys.path.insert(1, "..")

from praw import __version__  # noqa: E402

autodoc_typehints = "description"
copyright = datetime.today().strftime("%Y, Bryce Boe")
exclude_patterns = ["_build"]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]
html_css_files = ["praw8_migration.css"]
html_static_path = ["_static"]
html_theme = "furo"
intersphinx_mapping = {
    "prawcore": ("https://prawcore.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3", None),
}
nitpicky = True
project = "PRAW"
release = __version__
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
