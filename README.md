# Note!
A python wrapper for the Reddit API. 
I originally created this repo, and have since transferred ownership to the praw-dev (PRAW: Python Reddit API Wrapper) 
organization to allow this project to continue to grow. 
This fork is here to preserve old links, please head to the praw-dev/praw repo for the latest code.


# Introduction
This is a Python wrapper for Reddit's API, aiming to be as easy to use as
possible. Here's a quick peek, getting the first 5 submissions from the 'hot'
section of the 'opensource' subreddit.

```python
import reddit
r = reddit.Reddit(user_agent='my_cool_application')
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

    pip install reddit

Or via `easy-install`

    easy_install reddit

Or via `setup.py`

    python setup.py install


# Examples and Configuration
For a number of simple code examples, details on the Reddit API
Wrapper'sconfiguration files and links to projects which use this package see
the [wiki](https://github.com/mellort/reddit_api/wiki).


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
