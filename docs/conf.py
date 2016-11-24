import sys
sys.path.insert(0, "..")

from praw import __version__

copyright = '2014, Bryce Boe'
exclude_patterns = ['_build']
extensions = ['sphinx.ext.autodoc']
html_static_path = ['_static']
html_theme = 'default'
html_use_smartypants = True
htmlhelp_basename = 'PRAW'
master_doc = 'index'
nitpicky = True
project = 'PRAW'
pygments_style = 'sphinx'
release = __version__
source_suffix = '.rst'
suppress_warnings = ['image.nonlocal_uri']
version = '.'.join(__version__.split('.', 2)[:2])


def skip(app, what, name, obj, skip, options):
    if name in {'__call__', '__contains__', '__getitem__', '__init__',
                '__iter__', '__len__'}:
        return False
    return skip


def setup(app):
    app.connect('autodoc-skip-member', skip)
