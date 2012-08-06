# Introduction

PRAW, an acronym for "Python Reddit API Wrapper", is a python package that
allows for simple access to reddit's API.  PRAW aims to be as easy to use as
possible. Here's a quick peek, getting the first 5 submissions from the 'hot'
section of the 'opensource' subreddit.

```python
import praw
r = praw.Reddit(user_agent='my_cool_application')
submissions = r.get_subreddit('opensource').get_hot(limit=5)
[str(x) for x in submissions]
```

This will display something similar to the following:

```python
['10 :: Gun.io Debuts Group Funding for Open Source Projects\n Gun.io',
 '24 :: Support the Free Software Foundation',
 '67 :: The 10 Most Important Open Source Projects of 2011',
  '2 :: Open-source webOS is dead on arrival ',
 '85 :: Plan 9 - A distributed OS with a unified communication protocol and I/O driver model.  Wow.']
```

# Installation
You can install via `pip`

    pip install praw

Or via `easy_install`

    easy_install praw

Or via `setup.py`

    # First download or checkout the code then run
    python setup.py install

PRAW works with Python 2.6 or later.

Installation via `pip` or `easy_install` automatically installs PRAW's only
dependency, the module [six](http://pypi.python.org/pypi/six/). If you install 
via `setup.py` you'll need to install `six` manually.

# Examples and Configuration

For a number of simple code examples, details on PRAW's
configuration files and links to projects which use this package see the
[wiki](https://github.com/praw-dev/praw/wiki).


# FAQ
> Why is everything so slow?

Usually that has to do with how fast reddit is responding at the moment. Check
the site, see if it's responding quicker when accessing it in your browser.
Otherwise, we respect the "no more than one API call per two seconds" rule, so
if you're trying to do a bunch of quick requests in succession you're going to
be spaced out to one call per second. If you're having a specific issue besides
something covered by one of those two things, please let us know (or file a
ticket) and we'll check it out.


# License
All of the code contained here is licensed by the GNU GPLv3.
