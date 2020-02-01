Monitoring New Submissions With a Certain Flair
================================================

In January 2020, there was an outbreak of a coronavirus, called ``2019-nCoV``.
In order to know if we're at risk, we want to monitor new case posts and print
the titles of the posts to check if our home country or state has found a new
case. We also want to print the link to the submission so we can read the
contents if the post is a selftext or visit the linked website, and maybe even
read the comments, which might have more detailed information.

The major subreddit for discussion on the virus is called ``r/China_Flu``.
All new case posts are flaired with a certain flair, so we can use that flair
to check for submissions. Reddit allows you to search for all posts with a
specific flair, so we will use the method :meth:`.Subreddit.search` to find
new submissions. While PRAW creates default streams for us, we can also
make our own streams.

Step 1: Getting Started
~~~~~~~~~~~~~~~~~~~~~~~

Access to Reddit's API requires a set of OAuth2 credentials. Those credentials
are obtained by registering an application with Reddit. To register an
application and receive a set of OAuth2 credentials please follow only the
"First Steps" section of Reddit's `OAuth2 Quick Start Example`_ wiki page.

Once the credentials are obtained we can begin writing the post monitor. Start
by creating an instance of :class:`.Reddit`:

.. code-block:: python

   import praw

   reddit = praw.Reddit(user_agent='VIRUS CASE SCANNER (by /u/USERNAME)',
                        client_id='CLIENT_ID', client_secret="CLIENT_SECRET",
                        username='USERNAME', password='PASSWORD')

In addition to the OAuth2 credentials, the username and password of the Reddit
account that registered the application are required.

.. note:: This example demonstrates use of a *script* type application. For
   other application types please see Reddit's wiki page `OAuth2 App Types
   <https://github.com/reddit/reddit/wiki/oauth2-app-types>`_.

Step 2: Determining The Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The method :meth:`.Subreddit.search` takes parameters for ``query``, ``sort``,
``syntax`` and ``time_filter``, although we will not be using the last two.

The query must include the flair name. On Reddit, to search by the flair text,
you will include in the query ``flair:"Flair text"``. Therefore, if we want to
search for the flair ``New case``, our query could be ``flair:"New case"``.
Furthermore, if we only want to search for submissions that contain our home
country (as an example we will use ``Canada``). In such a case, just include
the name of the country before the ``flair:...`` part of the query
(``canada flair:"New case"`` in our example).

We also want to sort by new, because otherwise we will only obtain
old submissions, which we do not want. Therefore, our sort will be ``new``.

First, create the :class:`.Subreddit` instance.

.. code-block:: python

    virus_subreddit = reddit.subreddit("China_Flu")

Then, retrieve the search results.

.. code-block:: python

    query = 'canada flair:"New case"'
    results = virus_subreddit.search(query, sort="new")

Finally, print the title and url for each result.

.. code-block:: python

    for result in results:
        title = result.title
        link = result.permalink
        print("<Virus Scanner>: New submission found: "
        "https://www.reddit.com{link}".format(link=link))
        print("Submission title: {title}".format(title=title))

However, this will only work one time, so let's put it into a stream.

Step 3: Creating a custom stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create your own custom streams. In order to obtain the stream
generator, import it from the module ``praw.models.util``.

.. code-block:: python

    from praw.models.util import stream_generator

The stream generator takes a function, and a lot of other arguments, but for
the tutorial, those will not be utilized. In order to pass arguments to the
underlying function, we pass them in as keyword arguments to the stream
generator.

The stream generator argument, assuming that the variable ``query`` exists as a
string, would look like this:

.. code-block:: python

    result_stream = stream_generator(virus_subreddit.search, # our function
                                     query=query, # query argument
                                     sort="new") # sort

We can re-use the earlier code for printing the results, except this time,
the loop will never terminate, as the stream will continously fetch items.

.. code-block:: python

    for result in result_stream:
        title = result.title
        link = result.permalink
        print("<Virus Scanner>: New submission found: "
        "https://www.reddit.com{link}".format(link=link))
        print("Submission title: {title}".format(title=title))

Full Code
~~~~~~~~~
Here is the full code for the virus scanner:

.. literalinclude:: ../examples/virus_scanner.py
   :language: python

.. _OAuth2 Quick Start Example:
   https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps