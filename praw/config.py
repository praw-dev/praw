"""Provides the code to load PRAW's configuration file `praw.ini`."""
from os import path as op
from os import environ, getenv
import sys
from configparser import ConfigParser
from typing import Dict, Sequence


def get_praw_environment_settings() -> Dict[str, str]:
    return {k[len("praw_"):]: v for k, v in environ.items() if k.startswith("praw_")}

def get_potential_praw_ini_locations() -> Sequence[str]:
    inifile = 'praw.ini'

    tlp_dir = ''
    if __name__ != '__main__':
        top_level_package_name, _, _ = __name__.partition('.')
        tlp_module = sys.modules[top_level_package_name]
        tlp_dir = op.dirname(tlp_module.__file__)

    getenv2 = lambda key: getenv(key, '')
    location_components = [
        (tlp_dir,),  # Package default
        (getenv2('APPDATA'),),  # Windows
        (getenv2('HOME'), '.config'),  # Legacy Linux, and macOS
        (getenv2('XDG_CONFIG_HOME'),),  # Modern Linux
        ('.',),  # Current working directory
    ]

    locations = [
        op.join(*comps, inifile)
        for comps in location_components
        if comps[0]
    ]
    return locations

def get_praw_config(config: ConfigParser = None) -> ConfigParser:
    if config is None:
        config = ConfigParser()
    config.read(get_potential_praw_ini_locations())
    return config
