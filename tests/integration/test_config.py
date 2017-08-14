"""Test praw.config."""
from praw.models.reddit.submission import Submission 

import pytest

from . import IntegrationTest

class TestConfig(IntegrationTest):
  def test_store_json__submission__default_false(self):
    with self.recorder.use_cassette('TestSubmission.test_get'):
      submission = Submission(self.reddit, '3hahrw')
      submission._fetch()
      assert submission.json_dict is None

  def test_store_json__submission__true(self):
    self.reddit.config.store_json = True 
    with self.recorder.use_cassette('TestSubmission.test_get'):
      submission = Submission(self.reddit, '3hahrw')
      submission._fetch()
      assert submission.json_dict is not None
      assert submission.json_dict['id'] == '3hahrw'

