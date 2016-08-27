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
        prev_environment = {environment: None}
        for env_name in ['APPDATA', 'HOME', 'XDG_CONFIG_HOME']:
            if env_name in os.environ:
                prev_environment[env_name] = os.environ[env_name]
                del os.environ[env_name]
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
            for env_name in prev_environment:
                if prev_environment[env_name] is None:
                    del os.environ[env_name]
                else:
                    os.environ[env_name] = prev_environment[env_name]

    def test_check_for_updates__false(self):
        for value in [False, 'False', 'other']:
            config = Config('DEFAULT', check_for_updates=value)
            assert config.check_for_updates is False

    def test_custom__extra_values_set(self):
        config = Config('DEFAULT', user1='foo', user2='bar')
        assert config.custom == {'user1': 'foo', 'user2': 'bar'}

    def test_custom__no_extra_values_set(self):
        config = Config('DEFAULT')
        assert config.custom == {}

    def test_check_for_updates__true(self):
        for value in [True, '1', 'true', 'YES', 'on']:
            config = Config('DEFAULT', check_for_updates=value)
            assert config.check_for_updates is True

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
        config = Config('DEFAULT')
        assert config.short_url == 'https://redd.it'

    def test_short_url_not_defined(self):
        config = Config('DEFAULT', short_url=None)
        with pytest.raises(ClientException) as excinfo:
            config.short_url
        assert str(excinfo.value) == 'No short domain specified.'

    def test_unset_value_has_useful_string_representation(self):
        config = Config('DEFAULT')
        assert str(config.password) == 'NotSet'
