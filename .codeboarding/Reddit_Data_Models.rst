Reddit Data Models
==================

.. mermaid::

   graph LR
      praw_models_reddit_subreddit["praw.models.reddit.subreddit"]
      praw_models_reddit_submission["praw.models.reddit.submission"]
      praw_models_reddit_comment["praw.models.reddit.comment"]
      praw_models_reddit_redditor["praw.models.reddit.redditor"]
      praw_models_reddit_modmail["praw.models.reddit.modmail"]
      praw_models_reddit_live["praw.models.reddit.live"]
      praw_models_reddit_widgets["praw.models.reddit.widgets"]
      praw_models_reddit_collections["praw.models.reddit.collections"]
      praw_models_reddit_submission -- "retrieves associated" --> praw_models_reddit_comment
      praw_models_reddit_comment -- "accesses the parent" --> praw_models_reddit_submission

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

The `Reddit Data Models` subsystem, rooted in `praw.models.reddit`, provides a structured, Pythonic interface to various Reddit entities, abstracting the underlying API interactions. It aligns with the project's goal of offering a clean API Wrapper/Client Library by defining distinct objects for different Reddit resources.

praw.models.reddit.subreddit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Manages subreddit properties, moderation, content submission, flair, styles, and user relationships. It serves as a central hub for all subreddit-specific operations.

**Related Classes/Methods**:

* `praw.models.reddit.subreddit <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/subreddit.py>`_

praw.models.reddit.submission
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Manages post details, flair, moderation, and comment retrieval. It encapsulates all functionalities related to a single Reddit post.

**Related Classes/Methods**:

* `praw.models.reddit.submission <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/submission.py>`_

praw.models.reddit.comment
^^^^^^^^^^^^^^^^^^^^^^^^^^

Handles comment moderation and navigation to its parent or submission. It provides an interface for interacting with individual comments.

**Related Classes/Methods**:

* `praw.models.reddit.comment <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/comment.py>`_

praw.models.reddit.redditor
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Manages user streams and friendship status. It provides an interface for interacting with Reddit user profiles.

**Related Classes/Methods**:

* `praw.models.reddit.redditor <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/redditor.py>`_

praw.models.reddit.modmail
^^^^^^^^^^^^^^^^^^^^^^^^^^

Parses and manages modmail conversations, providing functionality for interacting with Reddit's internal moderation messaging system.

**Related Classes/Methods**:

* `praw.models.reddit.modmail <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/modmail.py>`_

praw.models.reddit.live
^^^^^^^^^^^^^^^^^^^^^^^

Manages Live Threads, handling invites, updates, and contributions for real-time event streams.

**Related Classes/Methods**:

* `praw.models.reddit.live <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/live.py>`_

praw.models.reddit.widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^

Provides an interface for interacting with subreddit widgets, including moderation and creation of different widget types.

**Related Classes/Methods**:

* `praw.models.reddit.widgets <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/widgets.py>`_

praw.models.reddit.collections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Manages post collections within a subreddit, providing an interface for creating, modifying, and retrieving curated groups of posts.

**Related Classes/Methods**:

* `praw.models.reddit.collections <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/collections.py>`_


FAQ
---

`See the FAQ <https://github.com/CodeBoarding/GeneratedOnBoardings/tree/main?tab=readme-ov-file#faq>`_
