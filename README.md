Introduction
------------

This is a Python wrapper for Reddit's API, aiming to be as easy to use as
possible. Here's a quick peek, getting the first 10 submissions from the 'hot'
section of the 'opensource' subreddit.

```python
import reddit
r = reddit.Reddit(user_agent='my_cool_application')
submissions = r.get_subreddit('opensource').get_hot(limit=5)
[str(x) for x in submissions]
```

this will display something similar to the following:

```python
['10 :: Gun.io Debuts Group Funding for Open Source Projects\n Gun.io',
 '24 :: Support the Free Software Foundation',
 '67 :: The 10 Most Important Open Source Projects of 2011',
  '2 :: Open-source webOS is dead on arrival ',
 '85 :: Plan 9 - A distributed OS with a unified communication protocol and I/O driver model.  Wow.']
```

Install
-------
You can install via `pip` 

    pip install reddit

Or via `setup.py`

    python setup.py install


A Few Short Examples
--------------------

0. Logging in:

    ```python
r.login('username', 'password')
```

0. Send a message (requires login):

    ```python
r.compose_message('bboe', 'Subject Line', 'You are awesome!')
```

0. Mark all unread messages as read (requires login):

    ```python
for msg in r.user.get_unread(limit=None):
        msg.mark_as_read()
```

0. Get the top submissions for r/python:

    ```python
submissions = r.get_subreddit('python').get_top(limit=10)
```

0. Get comments from a given submission:

    ```python
submission = submissions.next()
submission.comments
```

0. Comment on a submission (requires login):

    ```python
submission.add_comment('text')
```

0. Reply to a comment (requires login):

    ```python
comment = submission.comments[0]
comment.reply('test')
```

0. Voting (requires login):

    ```python
# item can be a comment or submission
item.upvote()
item.downvote()
item.clear_vote()
```

0. Deleting (requires login):

    ```python
#item can be a comment or submission
item.delete()
```

0. Saving a submission (requires login):

    ```python
submission.save()
submission.unsave()
```

0. Create a SELF submission (requires login):

    ```python
r.submit('reddit_api_test', 'submission title', text='body')
```

0. Create a URL submission (requires login):

    ```python
r.submit('reddit_api_test', 'Google!', url='http://google.com')
```

0. Get user karma:

    ```python
user = r.get_redditor('ketralnis')
user.link_karma
user.comment_karma
```

0. Get saved links (requires login):

    ```python
r.get_saved_links()
```

0. Get content newer than a comment or submission's id:

    ```python
r.get_subreddit('python').get_top(limit=None, place_holder=submission.id)
```

0. (Un)subscribe to a subreddit (requires login):

    ```python
r.get_subreddit('python').subscribe()
r.get_subreddit('python').unsubscribe()
```

0. (Un)friend a user:

    ```python
r.get_redditor('ketralnis').friend()
r.get_redditor('ketralnis').unfriend()
```

0. Create a subreddit:

    ```python
r.create_subreddit(short_title='MyIncredibleSubreddit',
                       full_title='my Incredibly Cool Subreddit',
                       description='It is incredible!')
```

0. Get flair mappings for a particular subreddit (requires mod privileges):

    ```python
item = r.get_subreddit('python').flair_list().next()
item['user']
item['flair_text']
item['flair_css_class']
```

0. Set / update user flair (requires mod privileges):

    ```python
r.get_subreddit('python').set_flair('bboe', 'text flair', 'css-class')
```

0. Clear user flair (requires mod privileges):

    ```python
r.get_subreddit('python').set_flair('bboe')
```

0. Bulk set user flair (requires mod privileges):

    ```python
flair_mapping = [{'user':'bboe', 'flair_text':'dev'},
                     {'user':'pyapitestuser3', 'flair_css_class':'css2'},
                     {'user':'pyapitestuser2', 'flair_text':'AWESOME',
                      'flair_css_class':'css'}]
r.get_subreddit('python').set_flair_csv(flair_mapping)
```

0. Add flair templates (requires mod privileges):

    ```python
r.get_subreddit('python').add_flair_template(text='editable', css_class='foo',
                                             text_editable=True)
```

0. Clear flair templates (requires mod privileges):

    ```python
r.get_subreddit('python').clear_flair_templates()
```

Extra usage info
----------

* All of the listings (list of stories on subreddit, etc.) are generators,
  *not* lists. If you need them to be lists, an easy way is to call `list()`
  with your variable as the argument.
* The default limit for fetching stories is 25. You can change this with the
  `limit` param. If you don't want a limit, set `limit=None`. This will return
  an infinite generator that will continue fetching stories until reddit
  hiccups (I wouldn't expect more than ~300 stories).

Example Applications/Scripts
----------------------------

Note: these all use very outdated versions of the API. 
Don't expect them to work with the latest version.
I recommend using them as reference only.

* A [comment
  tracker](http://github.com/mellort/reddit_comment_tracker/blob/master/comment_tracker.py),
  which repeatedly looks at new Reddit comments and can take an action if they
  meet a specified condition. The example use I gave is replying with an
  automated message if the body of a comment contains a certain word. (Novelty
  accounts, anyone?)
* An [account
  cloner](http://github.com/mellort/reddit_account_cloner/blob/master/account_cloner.py). Given
  two logins and passwords, it will transfer all of the saved links and
  subscribed subreddits from the first account to the second.
* A [comment generator](http://github.com/mellort/reddit_comment_bot): it pulls
  comments from Reddit, puts them in a Markov chain, and periodically outputs
  random statuses. The statuses can be viewed
  [here](http://identi.ca/redditbot/all).

I hope that this wrapper allows for many more quick and useful applications to
be made!

Dependencies
------------

* [setuptools](http://pypi.python.org/pypi/setuptools) is required to install reddit_api.

FAQ
------------

> Why is everything so slow?

Usually that has to do with how fast reddit is responding at the moment. Check
the site, see if it's responding quicker when accessing it in your browser.
Otherwise, we respect the "no more than one API call per two seconds" rule, so
if you're trying to do a bunch of quick requests in succession you're going to
be spaced out to one call per second. If you're having a specific issue besides
something covered by one of those two things, please let us know (or file a
ticket) and we'll check it out.

> I want to change the sort/time options for a given listing. How do I do that?

This currently isn't a part of the wrapper, but the `_get_sorter` method in
`helpers.py` is exactly what you want. The parameters you want to change are
`sort` and `time`. I'll add this to the wrapper shortly.

> I want a new feature!

File an enhacement request via github issues.

> Something doesn't work. What gives?

File an issue, I'll look into it.

> I want to help develop, but I'm lost. 

Send me a github message. I can help you get aquainted with the code base, and
maybe we can write a wiki page for others, too.


License
------------
All of the code contained here is licensed by the GNU GPLv3.
