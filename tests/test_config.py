"""Tests for Config class."""

import unittest
from praw import Config
from praw.errors import ClientException

try:
    import ConfigParser as configparser
except ImportError:
    import configparser  # NOQA pylint: disable=F0401


class ConfigTest(unittest.TestCase):
    def test_default_site(self):
        config = Config('reddit')
        self.assertEqual(0, config.log_requests)
        self.assertEqual(2, config.api_request_delay)
        self.assertEqual(None, config.user)
        self.assertEqual(None, config.pswd)

    def test_default_site__with_overrides(self):
        config = Config('reddit', log_requests=15, api_request_delay=21)
        self.assertEqual(15, config.log_requests)
        self.assertEqual(21, config.api_request_delay)

    def test_default_site__with_username_and_password(self):
        config = Config('reddit', user='foo', pswd='bar')
        self.assertEqual('foo', config.user)
        self.assertEqual('bar', config.pswd)

    def test_invalid_site(self):
        self.assertRaises(configparser.NoSectionError, Config, 'invalid')

    def test_local_site(self):
        config = Config('local_example')
        try:
            config.short_domain
            self.fail('Did not raise ClientException')
        except ClientException:
            pass
