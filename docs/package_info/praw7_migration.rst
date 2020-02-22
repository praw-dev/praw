Migrating to PRAW 7.X
=====================

Exception Handling
------------------

PRAW 7 introduced a fundamental change in how exceptions are recieved from
Reddit's API. Reddit can return multiple exceptions for one API action, and
as such, the previous :class:`.APIException` serves as a container for each of
the true exception objects. These objects are instances of
:class:`.RedditErrorItem`, and they contain the information of one "error" from
Reddit's API. They have the three data attributes that :class:`.APIException`
used to contain.

Most code regarding exceptions can be quickly fixed to work under the new
system. In the example code below, observe how attributes are accessed.

.. code-block:: python

    try:
        reddit.subreddit("test").submit("Test Title", url="invalidurl")
    except APIException as exception:
        print(exception.error_type)

This can generally be changed to

.. code-block:: python

    try:
        reddit.subreddit("test").submit("Test Title", url="invalidurl")
    except APIException as exception:
        print(exception[0].error_type)

However, this should not be done, as this will only work for one error. The
probability of Reddit's API returning multiple exceptions, especially on
submit actions, should be addressed. Rather, iterate over the exception,
and do the action on each item in the iterator.

.. code-block:: python

    try:
        reddit.subreddit("test").submit("Test Title", url="invalidurl")
    except APIException as exception:
        for subexception in exception:
            print(subexception.error_type)

Alternatively, the exceptions are provided to the exception constructor, so
printing the exception directly will also allow you to see all of the
exceptions.

.. code-block:: python

    try:
        reddit.subreddit("test").submit("Test Title", url="invalidurl")
    except APIException as exception:
        print(exception)