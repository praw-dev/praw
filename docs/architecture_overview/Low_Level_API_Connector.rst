Low Level Api Connector
=======================

.. mermaid::

   graph LR
      Reddit_Client["Reddit Client"]
      Low_Level_API_Connector["Low-Level API Connector"]
      Authentication_Module["Authentication Module"]
      Data_Models_Objects["Data Models/Objects"]
      Configuration_Management["Configuration Management"]
      Reddit_Client -- "utilizes" --> Low_Level_API_Connector
      Reddit_Client -- "depends on" --> Low_Level_API_Connector
      Authentication_Module -- "configures" --> Low_Level_API_Connector
      Authentication_Module -- "provides authentication context to" --> Low_Level_API_Connector
      Reddit_Client -- "interacts with" --> Authentication_Module
      Reddit_Client -- "uses" --> Data_Models_Objects
      Reddit_Client -- "loads settings via" --> Configuration_Management
      Data_Models_Objects -- "are populated by" --> Low_Level_API_Connector
      Authentication_Module -- "reads settings from" --> Configuration_Management
      click Reddit_Client href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/Reddit_Client.html" "Details"
      click Low_Level_API_Connector href "https://github.com/CodeBoarding/praw/blob/main/.codeboarding/Low_Level_API_Connector.html" "Details"

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

The `praw` library provides a high-level, Pythonic interface for interacting with the Reddit API. At its core, the `Reddit Client` acts as the primary orchestrator, managing user requests and coordinating with other internal components. It leverages an `Authentication Module` to handle various OAuth2 flows and token management, ensuring secure access to Reddit resources. `Configuration Management` centralizes the loading and parsing of settings, making the client adaptable to different environments. All interactions with Reddit's data are facilitated through `Data Models/Objects`, which abstract API responses into intuitive Python objects. For the actual network communication and low-level OAuth2 intricacies, `praw` relies on the `Low-Level API Connector` (prawcore), an external dependency that handles the complexities of HTTP requests and responses, thereby decoupling `praw` from the underlying network layer.

Reddit Client
^^^^^^^^^^^^^

:ref:`Expand <Reddit_Client>`

The primary entry point for users to interact with the Reddit API. It orchestrates calls to other components to fulfill user requests, providing a high-level, Pythonic interface to Reddit resources.

**Related Classes/Methods**:

* `praw.Reddit <https://github.com/CodeBoarding/praw/blob/main/praw/reddit.py>`_

Low-Level API Connector
^^^^^^^^^^^^^^^^^^^^^^^

:ref:`Expand <Low_Level_API_Connector>`

An external dependency, `prawcore`, which is solely responsible for handling the low-level HTTP communication with the Reddit API. It manages the actual network requests, responses, and the intricacies of OAuth2 authentication flows, abstracting these complexities from the higher-level `praw` library.

**Related Classes/Methods**:

* `prawcore:527-546 <https://github.com/CodeBoarding/praw/blob/main/praw/reddit.py#L527-L546>`_

Authentication Module
^^^^^^^^^^^^^^^^^^^^^

Manages the various OAuth2 authentication flows (e.g., script, installed app, web app) and handles the storage and refreshing of access tokens.

**Related Classes/Methods**:

* `praw.auth <https://github.com/CodeBoarding/praw/blob/main/praw/models/auth.py>`_

Data Models/Objects
^^^^^^^^^^^^^^^^^^^

Represents Reddit API resources (e.g., `Submission`, `Comment`, `Subreddit`, `User`) as Python objects, providing attribute access and methods for interaction.

**Related Classes/Methods**:

* `praw.models.submission.Submission <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/submission.py>`_
* `praw.models.subreddit.Subreddit <https://github.com/CodeBoarding/praw/blob/main/praw/models/reddit/subreddit.py>`_

Configuration Management
^^^^^^^^^^^^^^^^^^^^^^^^

Handles the loading, parsing, and management of configuration settings (e.g., client ID, client secret, user agent) from various sources (e.g., `praw.ini`, environment variables).

**Related Classes/Methods**:

* `praw.config <https://github.com/CodeBoarding/praw/blob/main/praw/config.py>`_
