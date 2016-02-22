"""Provides the code to load PRAW's configuration file `praw.ini`."""

import os
import sys
from six.moves import configparser


def _load_configuration():
    """Attempt to load settings from various praw.ini files."""
    config = configparser.RawConfigParser()
    module_dir = os.path.dirname(sys.modules[__name__].__file__)
    if 'APPDATA' in os.environ:  # Windows
        os_config_path = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:  # Modern Linux
        os_config_path = os.environ['XDG_CONFIG_HOME']
    elif 'HOME' in os.environ:  # Legacy Linux
        os_config_path = os.path.join(os.environ['HOME'], '.config')
    else:
        os_config_path = None
    locations = [os.path.join(module_dir, 'praw.ini'), 'praw.ini']
    if os_config_path is not None:
        locations.insert(1, os.path.join(os_config_path, 'praw.ini'))
    if not config.read(locations):
        raise Exception('Could not find config file in any of: {0}'
                        .format(locations))
    return config
CONFIG = _load_configuration()
del _load_configuration
