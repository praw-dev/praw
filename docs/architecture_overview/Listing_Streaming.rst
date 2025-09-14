Listing Streaming
=================

.. mermaid::

   graph LR
      ListingGenerator["ListingGenerator"]
      BaseListingMixin["BaseListingMixin"]
      SubredditListingMixin["SubredditListingMixin"]
      RedditorListingMixin["RedditorListingMixin"]
      StreamGenerator["StreamGenerator"]
      RedditorsStream["RedditorsStream"]
      InboxStream["InboxStream"]
      SubredditContentStream["SubredditContentStream"]
      SubredditListingMixin -- "specializes" --> BaseListingMixin
      RedditorListingMixin -- "specializes" --> BaseListingMixin
      BaseListingMixin -- "utilizes" --> ListingGenerator
      SubredditListingMixin -- "utilizes" --> ListingGenerator
      RedditorListingMixin -- "utilizes" --> ListingGenerator
      RedditorsStream -- "leverages" --> StreamGenerator
      InboxStream -- "leverages" --> StreamGenerator
      SubredditContentStream -- "leverages" --> StreamGenerator

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

The PRAW library's data retrieval architecture is primarily composed of two distinct but complementary patterns: listing generation and stream generation. The ListingGenerator forms the backbone for paginated data retrieval, efficiently fetching and iterating through large datasets from the Reddit API. This core functionality is extended and specialized by BaseListingMixin, SubredditListingMixin, and RedditorListingMixin, which provide context-specific listing capabilities for general, subreddit, and redditor content, respectively. For real-time data, the StreamGenerator (implemented as stream_generator utility) offers a robust mechanism for continuous data delivery, handling deduplication and rate limiting. This utility is leveraged by higher-level stream methods within Redditors, Inbox, and Subreddits classes, providing user-friendly entry points for accessing live streams of redditors, inbox messages, and subreddit content. This dual approach ensures comprehensive and efficient access to both historical and real-time Reddit data.

ListingGenerator
^^^^^^^^^^^^^^^^

Manages the iteration and pagination of items from Reddit API responses. It handles fetching data in batches, extracting relevant sub-lists, and providing an iterable interface to the user, abstracting away pagination details. This component is crucial for efficiently handling large datasets from the Reddit API.

**Related Classes/Methods**:

* `ListingGenerator:17-103 <https://github.com/CodeBoarding/praw/blob/main/praw/models/listing/generator.py#L17-L103>`_

BaseListingMixin
^^^^^^^^^^^^^^^^

Provides foundational listing methods such as `hot`, `new`, `top`, and `controversial`. It prepares generic API requests and validates time filters applicable across various Reddit resources, serving as a common interface for listing operations.

**Related Classes/Methods**:

* `BaseListingMixin:15-149 <https://github.com/CodeBoarding/praw/blob/main/praw/models/listing/mixins/base.py#L15-L149>`_

SubredditListingMixin
^^^^^^^^^^^^^^^^^^^^^

Specializes listing functionality for subreddit-specific content, including comments and submissions within a subreddit. It determines appropriate API paths for subreddit-related data, extending the base listing capabilities.

**Related Classes/Methods**:

* `SubredditListingMixin:49-73 <https://github.com/CodeBoarding/praw/blob/main/praw/models/listing/mixins/subreddit.py#L49-L73>`_

RedditorListingMixin
^^^^^^^^^^^^^^^^^^^^

Specializes listing functionality for redditor-specific content, such as comments and submissions made by a particular user. It creates sub-listings tailored to user activity, providing a user-centric view of Reddit data.

**Related Classes/Methods**:

* `RedditorListingMixin:35-185 <https://github.com/CodeBoarding/praw/blob/main/praw/models/listing/mixins/redditor.py#L35-L185>`_

StreamGenerator
^^^^^^^^^^^^^^^

This component, implemented as the `stream_generator` function, provides a generic, low-level mechanism for continuously yielding new items from a source. It manages the stream's state, handles deduplication using a `BoundedSet`, and incorporates exponential backoff for rate limiting, forming the core engine for all streaming operations. This is the fundamental utility for real-time data.

**Related Classes/Methods**:

* `stream_generator:36-163 <https://github.com/CodeBoarding/praw/blob/main/praw/models/util.py#L36-L163>`_

RedditorsStream
^^^^^^^^^^^^^^^

Represents the `stream` method within the `Redditors` class, acting as an entry point for initiating and managing a continuous stream of new redditors as they are created or become active. It provides a high-level interface for accessing real-time user data by leveraging the `stream_generator` utility.

**Related Classes/Methods**:

* `Redditors.stream:93-104 <https://github.com/CodeBoarding/praw/blob/main/praw/models/redditors.py#L93-L104>`_

InboxStream
^^^^^^^^^^^

Represents the `stream` method within the `Inbox` class, acting as an entry point for initiating and managing a continuous stream of unread inbox messages for the authenticated user. This component is vital for real-time notification and interaction features, leveraging the `stream_generator` utility.

**Related Classes/Methods**:

* `Inbox.stream:229-247 <https://github.com/CodeBoarding/praw/blob/main/praw/models/inbox.py#L229-L247>`_

SubredditContentStream
^^^^^^^^^^^^^^^^^^^^^^

Represents the `stream` method within the `Subreddits` class, providing access to streams of content related to a specific subreddit, including specialized moderation streams. This allows for real-time monitoring of activity within a subreddit by leveraging the `stream_generator` utility.

**Related Classes/Methods**:

* `Subreddits.stream:124-133 <https://github.com/CodeBoarding/praw/blob/main/praw/models/subreddits.py#L124-L133>`_
