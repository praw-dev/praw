Api Interaction Facades
=======================

.. mermaid::

   graph LR
      Subreddit["Subreddit"]
      Redditor["Redditor"]
      Modmail["Modmail"]
      ModNotes["ModNotes"]
      Auth["Auth"]
      ListingGenerator["ListingGenerator"]
      stream_generator["stream_generator"]
      Subreddit -- "delegates to" --> Modmail
      Subreddit -- "interacts with" --> ModNotes
      Subreddit -- "utilizes" --> ListingGenerator
      Subreddit -- "leverages" --> stream_generator
      Subreddit -- "relies on" --> Auth
      Redditor -- "utilizes" --> ListingGenerator
      Redditor -- "leverages" --> stream_generator
      Redditor -- "relies on" --> Auth
      Modmail -- "relies on" --> Auth
      ModNotes -- "relies on" --> Auth
      ListingGenerator -- "relies on" --> Auth
      stream_generator -- "relies on" --> Auth

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

The `API Interaction Facades` subsystem encompasses high-level, domain-specific interfaces for interacting with the Reddit API. It abstracts complex operations and data retrieval patterns, grouping functionalities related to listing/streaming, subreddit management, moderation tools, and user/authentication specific actions.

Subreddit
^^^^^^^^^

Primary facade for all subreddit-related operations, including content submission, moderation, flair management, appearance customization, and data retrieval. It provides a high-level interface for interacting with a specific subreddit.

**Related Classes/Methods**:

* `praw.models.reddit.subreddit.Subreddit <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/subreddit.py>`_

Redditor
^^^^^^^^

Represents a Reddit user and provides methods for user-specific actions such as profile interaction, friendship management, and accessing user-generated content (submissions, comments).

**Related Classes/Methods**:

* `praw.models.reddit.redditor.Redditor <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/redditor.py>`_

Modmail
^^^^^^^

Manages modmail conversations within a specific subreddit, enabling functionalities like reading, replying to, and managing modmail threads.

**Related Classes/Methods**:

* `praw.models.reddit.modmail.Modmail <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/modmail.py>`_

ModNotes
^^^^^^^^

Facilitates the creation, retrieval, and deletion of moderator notes associated with various Reddit entities (e.g., users, submissions).

**Related Classes/Methods**:

* `praw.models.mod_notes.ModNotes <https://github.com/CodeBoarding/praw/blob/main/praw/models/mod_notes.py>`_

Auth
^^^^

Manages the authentication and authorization processes with the Reddit API, ensuring all outgoing requests are properly credentialed and secure.

**Related Classes/Methods**:

* `praw.models.auth.Auth:11-125 <https://github.com/CodeBoarding/praw/blob/main/praw/models/auth.py#L11-L125>`_

ListingGenerator
^^^^^^^^^^^^^^^^

Provides an iterable interface for fetching paginated data from various Reddit API endpoints, handling the underlying pagination logic transparently.

**Related Classes/Methods**:

* `praw.models.listing.generator.ListingGenerator:17-103 <https://github.com/CodeBoarding/praw/blob/main/praw/models/listing/generator.py#L17-L103>`_

stream_generator
^^^^^^^^^^^^^^^^

Offers a resilient and generic streaming mechanism for continuous data retrieval from Reddit, incorporating features like rate limiting, duplicate detection, and exponential backoff for robust operation.

**Related Classes/Methods**:

* `praw.models.util.stream_generator:36-163 <https://github.com/CodeBoarding/praw/blob/main/praw/models/util.py#L36-L163>`_


FAQ
---

`See the FAQ <https://github.com/CodeBoarding/GeneratedOnBoardings/tree/main?tab=readme-ov-file#faq>`_
