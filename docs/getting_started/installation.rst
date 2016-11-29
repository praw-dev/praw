Installing PRAW
===============

PRAW supports python 2.7, 3.3, 3.4, and 3.5. The recommended way to install
PRAW is via ``pip``.

.. code-block:: bash

   pip install praw

.. note:: Depending on your system, you may need to use ``pip3`` to install
          packages for python 3.

.. warning:: Avoid using ``sudo`` to install packages. Do you `really` trust
             this package?

For instructions on installing python and pip see "The Hitchhiker's Guide to
Python" `Installation Guides
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

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

Is there a feature that was recently merged into PRAW that you cannot wait to
take advantage of? If so, you can install PRAW directly from github like so:

.. code-block:: bash

   pip install --upgrade https://github.com/praw-dev/praw/archive/master.zip
