Reddit Data Models
==================

.. mermaid::

   graph LR
      Submission["Submission"]
      Comment["Comment"]
      Redditor["Redditor"]
      Subreddit["Subreddit"]
      SubmissionModeration["SubmissionModeration"]
      CommentModeration["CommentModeration"]
      RedditorStream["RedditorStream"]
      SubredditModeration["SubredditModeration"]
      Submission -- "contains" --> Comment
      Submission -- "interacts with" --> SubmissionModeration
      Comment -- "associated with" --> Submission
      Comment -- "interacts with" --> CommentModeration
      Redditor -- "provides access to" --> RedditorStream
      Subreddit -- "contains" --> Submission
      Subreddit -- "interacts with" --> SubredditModeration
      SubmissionModeration -- "acts upon" --> Submission
      CommentModeration -- "acts upon" --> Comment
      RedditorStream -- "provides data streams related to" --> Redditor
      SubredditModeration -- "acts upon" --> Subreddit

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

The PRAW `reddit.models` subsystem provides a structured object-oriented interface for interacting with the Reddit API. Core components like `Submission`, `Comment`, `Redditor`, and `Subreddit` serve as primary data models, encapsulating Reddit entities and their associated functionalities. These core models are augmented by specialized moderation components (`SubmissionModeration`, `CommentModeration`, `SubredditModeration`) that provide administrative capabilities, and stream components (`RedditorStream`) for accessing dynamic content. The system is designed around clear object relationships, where entities like `Subreddit` contain `Submission`s, and `Submission`s contain `Comment`s, facilitating intuitive navigation and interaction with Reddit data. Moderation components act directly upon their respective core entities, enabling a clear separation of concerns between data representation and administrative actions.

Submission
^^^^^^^^^^

Represents a Reddit post, encapsulating its data (e.g., title, content, author, subreddit) and providing methods for interaction (e.g., voting, replying, editing). It serves as the primary interface for submission-specific data and actions.

**Related Classes/Methods**:

* `Submission <https://github.com/CodeBoarding/praw/blob/main/docs/examples/lmgtfy_bot.py>`_

Comment
^^^^^^^

Represents a Reddit comment, managing its content, author, and position within a discussion thread. It provides methods for managing comment content and its hierarchical position.

**Related Classes/Methods**:

* `Comment:582-596 <https://github.com/CodeBoarding/praw/blob/main/praw/reddit.py#L582-L596>`_

Redditor
^^^^^^^^

Represents a Reddit user, offering access to their profile, activity history (e.g., submissions, comments), and relationships with other users or subreddits.

**Related Classes/Methods**:

* `Redditor:810-819 <https://github.com/CodeBoarding/praw/blob/main/praw/reddit.py#L810-L819>`_

Subreddit
^^^^^^^^^

Represents a Reddit community, serving as a facade for managing subreddit settings, content, and user interactions within that community. It provides access to posts, moderation tools, and community-specific data.

**Related Classes/Methods**:

* `Subreddit <https://github.com/CodeBoarding/praw/blob/main/docs/examples/lmgtfy_bot.py>`_

SubmissionModeration
^^^^^^^^^^^^^^^^^^^^

Provides moderation functionalities specifically for a `Submission` object, enabling actions such as approving, removing, locking, or distinguishing posts.

**Related Classes/Methods**:

* `SubmissionModeration:93-392 <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/submission.py#L93-L392>`_

CommentModeration
^^^^^^^^^^^^^^^^^

Provides moderation functionalities specifically for a `Comment` object, enabling actions like approving, removing, or distinguishing comments.

**Related Classes/Methods**:

* `CommentModeration:314-350 <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/comment.py#L314-L350>`_

RedditorStream
^^^^^^^^^^^^^^

Offers access to various streams of content related to a `Redditor`, such as their submissions, comments, or saved items, allowing for real-time or historical data retrieval.

**Related Classes/Methods**:

* `RedditorStream:412-457 <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/redditor.py#L412-L457>`_

SubredditModeration
^^^^^^^^^^^^^^^^^^^

Provides comprehensive moderation tools for a `Subreddit`, including managing users (e.g., banning, muting), flair, and content policies at the community level.

**Related Classes/Methods**:

* `SubredditModeration:82-199 <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/user_subreddit.py#L82-L199>`_


FAQ
---

`See the FAQ <https://github.com/CodeBoarding/GeneratedOnBoardings/tree/main?tab=readme-ov-file#faq>`_
