.. _environment_variables:

PRAW Environment Variables
==========================

The highest priority configuration options can be passed to a program via
environment variables prefixed with ``praw_``.

For example, you can invoke your script as follows:

.. code-block:: shell

   praw_username=bboe praw_password=not_my_password python my_script.py

The ``username`` and ``password`` provided via environment variables will
override any such values passed directly when initializing an instance of
:class:`.Reddit`, as well as any such values contained in a ``praw.ini`` file.

All :ref:`configuration_options` can be provided in this manner, except for
custom options.
