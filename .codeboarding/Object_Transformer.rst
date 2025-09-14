Object Transformer
==================

.. mermaid::

   graph LR
      Objector_Class["Objector Class"]
      Objector_objectify_Method["Objector.objectify Method"]
      Objector__objectify_dict_Method["Objector._objectify_dict Method"]
      Objector_check_error_Method["Objector.check_error Method"]
      Objector_parse_error_Method["Objector.parse_error Method"]
      Objector_Class -- "orchestrates" --> Objector_objectify_Method
      Objector_Class -- "orchestrates" --> Objector__objectify_dict_Method
      Objector_Class -- "orchestrates" --> Objector_check_error_Method
      Objector_Class -- "orchestrates" --> Objector_parse_error_Method
      Objector_objectify_Method -- "delegates to" --> Objector__objectify_dict_Method
      Objector_objectify_Method -- "invokes" --> Objector_check_error_Method
      Objector_check_error_Method -- "calls" --> Objector_parse_error_Method

| |codeboarding-badge| |demo-badge| |contact-badge|

.. |codeboarding-badge| image:: https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square
   :target: https://github.com/CodeBoarding/CodeBoarding
.. |demo-badge| image:: https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square
   :target: https://www.codeboarding.org/demo
.. |contact-badge| image:: https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square
   :target: mailto:contact@codeboarding.org

Details
-------

The `Object Transformer` subsystem is primarily defined by the `praw.objector` module, specifically the `Objector` class and its associated methods. Its core responsibility is to convert raw JSON data received from the Reddit API into structured, type-safe PRAW Python objects, while also handling API-specific error detection and parsing.

Objector Class
^^^^^^^^^^^^^^

Acts as the central facade and orchestrator for the entire objectification process. It manages the conversion of various raw data types (dictionaries, lists, booleans, etc.) into their corresponding PRAW objects and integrates error checking.

**Related Classes/Methods**:

* `praw.objector.Objector:17-263 <https://github.com/CodeBoarding/praw/blob/main/praw/objector.py#L17-L263>`_

Objector.objectify Method
^^^^^^^^^^^^^^^^^^^^^^^^^

Serves as the main public entry point for initiating the transformation of raw data. It intelligently handles different input types (e.g., `None`, `list`, `bool`, `dict`) and directs the flow to appropriate internal methods, including an initial check for embedded API errors.

**Related Classes/Methods**:

* `praw.objector.Objector:objectify <https://github.com/CodeBoarding/praw/blob/main/praw/objector.py>`_

Objector._objectify_dict Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specializes in converting dictionary-structured data, which is typical for Reddit API responses, into specific PRAW objects. It contains conditional logic to identify the precise type of Reddit object (e.g., `ModmailConversation`, `Subreddit`, `Redditor`) based on key fields and applies the relevant parsing logic.

**Related Classes/Methods**:

* `praw.objector.Objector:_objectify_dict <https://github.com/CodeBoarding/praw/blob/main/praw/objector.py>`_

Objector.check_error Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Examines the raw input data to determine if it represents an API error response. If an error is detected, it triggers the raising of a `RedditAPIException`, ensuring that API-level issues are properly surfaced.

**Related Classes/Methods**:

* `praw.objector.Objector:check_error <https://github.com/CodeBoarding/praw/blob/main/praw/objector.py>`_

Objector.parse_error Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extracts and formats detailed error messages from the raw API response, converting them into a structured `RedditAPIException` instance. This provides clear and actionable error information to the user.

**Related Classes/Methods**:

* `praw.objector.Objector:parse_error <https://github.com/CodeBoarding/praw/blob/main/praw/objector.py>`_
