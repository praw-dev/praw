# This file is part of reddit_api.
#
# reddit_api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# reddit_api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with reddit_api.  If not, see <http://www.gnu.org/licenses/>.

import reddit.backport  # pylint: disable-msg=W0611

import os
import sys
from six.moves import configparser


def _load_configuration():
    config = configparser.RawConfigParser()
    module_dir = os.path.dirname(sys.modules[__name__].__file__)
    if 'APPDATA' in os.environ:  # Windows
        os_config_path = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:  # Modern Linux
        os_config_path = os.environ['XDG_CONFIG_HOME']
    else:  # Legacy Linux
        os_config_path = os.path.join(os.environ['HOME'], '.config')
    locations = [os.path.join(module_dir, 'reddit_api.cfg'),
                 os.path.join(os_config_path, 'reddit_api', 'reddit_api.cfg'),
                 'reddit_api.cfg']
    if not config.read(locations):
        raise Exception('Could not find config file in any of: %s' % locations)
    return config
CONFIG = _load_configuration()
