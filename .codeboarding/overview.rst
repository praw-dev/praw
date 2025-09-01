Overview
========

.. mermaid::

   graph LR
      API_Client_Core["API Client Core"]
      Configuration_Manager["Configuration Manager"]
      Object_Hydrator["Object Hydrator"]
      Reddit_Data_Models["Reddit Data Models"]
      API_Interaction_Facades["API Interaction Facades"]
      Configuration_Manager -- "provides settings to" --> API_Client_Core
      API_Client_Core -- "reads configuration from" --> Configuration_Manager
      API_Interaction_Facades -- "sends requests via" --> API_Client_Core
      API_Client_Core -- "executes actions for" --> API_Interaction_Facades
      API_Client_Core -- "sends raw API response to" --> Object_Hydrator
      Object_Hydrator -- "returns PRAW objects to" --> API_Client_Core
      API_Client_Core -- "creates and populates" --> Reddit_Data_Models
      API_Interaction_Facades -- "operates on" --> Reddit_Data_Models
      Reddit_Data_Models -- "are managed by" --> API_Interaction_Facades
      Reddit_Data_Models -- "initiate requests via" --> API_Client_Core
      click API_Client_Core href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/API_Client_Core.html" "Details"
      click Configuration_Manager href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/Configuration_Manager.html" "Details"
      click Object_Hydrator href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/Object_Hydrator.html" "Details"
      click Reddit_Data_Models href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/Reddit_Data_Models.html" "Details"
      click API_Interaction_Facades href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/API_Interaction_Facades.html" "Details"

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

PRAW (Python Reddit API Wrapper) is structured around a clear separation of concerns, facilitating robust and flexible interaction with the Reddit API. At its core, the API Client Core (`praw.reddit.Reddit`) serves as the central communication hub, managing all HTTP requests, authentication, and rate limiting. It relies on the Configuration Manager (`praw.config.Config`) to load and provide necessary settings, ensuring proper API access.

Upon receiving raw JSON responses from the Reddit API, the API Client Core forwards this data to the Object Hydrator (`praw.objector.Objector`). The Object Hydrator is responsible for transforming these generic JSON structures into rich, interactive Python objects, which are instances of the Reddit Data Models (e.g., `praw.models.reddit.submission.Submission`, `praw.models.reddit.comment.Comment`, `praw.models.reddit.redditor.Redditor`, `praw.models.reddit.subreddit.Subreddit`). These models encapsulate Reddit entities and provide methods for further interaction.

To simplify complex API operations, API Interaction Facades provide high-level, domain-specific interfaces. These facades, such as `praw.models.listing.generator.ListingGenerator` for listing content, `praw.models.util.stream_generator` for streaming, and various methods within `praw.models.reddit.subreddit.Subreddit`, `praw.models.reddit.modmail`, `praw.models.mod_notes`, `praw.models.reddit.redditor.Redditor`, and `praw.models.auth.Auth`, abstract the underlying API calls. They send requests through the API Client Core and operate on the Reddit Data Models, allowing developers to interact with Reddit entities in an intuitive, object-oriented manner. The Reddit Data Models themselves can also initiate requests back through the API Client Core for entity-specific actions.

API Client Core
^^^^^^^^^^^^^^^

:ref:`Expand <API_Client_Core>`

The central component for all Reddit API communication, handling HTTP requests, authentication, and rate limiting. It acts as the primary interface for other components to communicate with Reddit.

**Related Classes/Methods**:

* `praw.reddit.Reddit:57-901 <https://github.com/CodeBoarding/praw/blob/main/praw/reddit.py#L57-L901>`_

Configuration Manager
^^^^^^^^^^^^^^^^^^^^^

:ref:`Expand <Configuration_Manager>`

Responsible for loading, parsing, and providing PRAW's configuration settings from various sources (e.g., `praw.ini`, environment variables).

**Related Classes/Methods**:

* `praw.config.Config <https://github.com/CodeBoarding/praw/blob/main/praw/config.py>`_

Object Hydrator
^^^^^^^^^^^^^^^

:ref:`Expand <Object_Hydrator>`

Transforms raw JSON data received from the Reddit API into rich, interactive Python objects (PRAW models), converting generic API responses into type-safe and method-rich objects.

**Related Classes/Methods**:

* `praw.objector.Objector:17-263 <https://github.com/CodeBoarding/praw/blob/main/praw/objector.py#L17-L263>`_

Reddit Data Models
^^^^^^^^^^^^^^^^^^

:ref:`Expand <Reddit_Data_Models>`

A comprehensive collection of classes representing various Reddit entities (e.g., `Submission`, `Comment`, `Redditor`, `Subreddit`). These objects encapsulate data and provide entity-specific methods for interaction.

**Related Classes/Methods**:

* `praw.models.reddit.submission.Submission <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/submission.py>`_
* `praw.models.reddit.comment.Comment <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/comment.py>`_
* `praw.models.reddit.redditor.Redditor <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/redditor.py>`_
* `praw.models.reddit.subreddit.Subreddit <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/subreddit.py>`_

API Interaction Facades
^^^^^^^^^^^^^^^^^^^^^^^

:ref:`Expand <API_Interaction_Facades>`

Provides high-level, domain-specific interfaces for interacting with the Reddit API, abstracting complex operations and data retrieval patterns. This component groups functionalities like listing/streaming, subreddit management, moderation tools, and user/authentication specific actions.

**Related Classes/Methods**:

* `praw.models.listing.generator.ListingGenerator:17-103 <https://github.com/CodeBoarding/praw/blob/main/praw/models/listing/generator.py#L17-L103>`_
* `praw.models.util.stream_generator:36-163 <https://github.com/CodeBoarding/praw/blob/main/praw/models/util.py#L36-L163>`_
* `praw.models.reddit.subreddit.Subreddit <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/subreddit.py>`_
* `praw.models.reddit.modmail <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/modmail.py>`_
* `praw.models.mod_notes <https://github.com/CodeBoarding/praw/blob/main/praw/models/mod_notes.py>`_
* `praw.models.reddit.redditor.Redditor <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/redditor.py>`_
* `praw.models.auth.Auth:11-125 <https://github.com/CodeBoarding/praw/blob/main/praw/models/auth.py#L11-L125>`_


FAQ
---

`See the FAQ <https://github.com/CodeBoarding/GeneratedOnBoardings/tree/main?tab=readme-ov-file#faq>`_
