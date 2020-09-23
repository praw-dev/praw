Installing PRAW
===============

PRAW supports Python 3.6+. The recommended way to install PRAW is via ``pip``.

.. code-block:: bash

    pip install praw

.. note::

    Depending on your system, you may need to use ``pip3`` to install packages for
    Python 3.

.. warning::

    Avoid using ``sudo`` to install packages. Do you `really` trust this package?

For instructions on installing Python and pip see "The Hitchhiker's Guide to Python"
`Installation Guides <https://docs.python-guide.org/en/latest/starting/installation/>`_.

Updating PRAW
-------------

PRAW can be updated by running:

.. code-block:: bash

    pip install --upgrade praw

Installing Older Versions
-------------------------

Older versions of PRAW can be installed by specifying the version number as
part of the installation command:

.. code-block:: bash

    pip install praw==3.6.0

Installing the Latest Development Version
-----------------------------------------

Is there a feature that was recently merged into PRAW that you cannot wait to take
advantage of? If so, you can install PRAW directly from GitHub like so:

.. code-block:: bash

    pip install --upgrade https://github.com/praw-dev/praw/archive/master.zip

You can also directly clone a copy of the repository using git, like so:

.. code-block:: bash

    pip install --upgrade git+https://github.com/praw-dev/praw.git
