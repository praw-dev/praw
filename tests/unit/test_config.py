import os
import sys

import mock
import pytest
from praw.config import Config
from praw.exceptions import ClientException


class TestConfig(object):
    @staticmethod
    def _assert_config_read(environment, mock_config):
        mock_instance = mock_config.return_value
        Config.CONFIG = None  # Force config file reload
        prev_environment = os.environ.get(environment)
        os.environ[environment] = '/MOCK'

        module_dir = os.path.dirname(sys.modules['praw'].__file__)
        environ_path = os.path.join(
            '/MOCK', '.config' if environment == 'HOME' else '', 'praw.ini')
        locations = [os.path.join(module_dir, 'praw.ini'), environ_path,
                     'praw.ini']

        try:
            Config._load_config()
            mock_instance.read.assert_called_with(locations)
        finally:
            Config.CONFIG = None  # Force config file reload
            if prev_environment:
                os.environ[environment] = prev_environment
            else:
                del os.environ[environment]

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_load_ini_from_appdata(self, mock_config):
        self._assert_config_read('APPDATA', mock_config)

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_load_ini_from_home(self, mock_config):
        self._assert_config_read('HOME', mock_config)

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_load_ini_from_xdg_config_home(self, mock_config):
        self._assert_config_read('XDG_CONFIG_HOME', mock_config)

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_load_ini_with_no_config_directory(self, mock_config):
        mock_instance = mock_config.return_value
        Config.CONFIG = None  # Force config file reload

        prev_environment = {}
        for key in ['APPDATA', 'HOME', 'XDG_CONFIG_HOME']:
            if key in os.environ:
                prev_environment[key] = os.environ[key]
                del os.environ[key]

        module_dir = os.path.dirname(sys.modules['praw'].__file__)
        locations = [os.path.join(module_dir, 'praw.ini'), 'praw.ini']

        try:
            Config._load_config()
            mock_instance.read.assert_called_with(locations)
        finally:
            Config.CONFIG = None  # Force config file reload
            for key, value in prev_environment.items():
                os.environ[key] = value

    def test_short_url(self):
        config = Config('reddit')
        assert config.short_url == 'https://redd.it'

    def test_short_url_not_defined(self):
        config = Config('reddit', short_url=None)
        with pytest.raises(ClientException) as excinfo:
            config.short_url
        assert str(excinfo.value) == 'No short domain specified.'
