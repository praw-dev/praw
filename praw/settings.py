# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from praw.compat import configparser  # pylint: disable-msg=E0611


def _load_configuration():
    config = configparser.RawConfigParser()
    module_dir = os.path.dirname(sys.modules[__name__].__file__)
    if 'APPDATA' in os.environ:  # Windows
        os_config_path = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:  # Modern Linux
        os_config_path = os.environ['XDG_CONFIG_HOME']
    elif 'HOME' in os.environ: # Legacy Linux
        os_config_path = os.path.join(os.environ['HOME'], '.config')
    else:
        os_config_path = None
    locations = [os.path.join(module_dir, 'praw.ini'), 
                'praw.ini']
    if os_config_path is not None:
        locations.insert(1,os.path.join(os_config_path, 'praw.ini'))
    if not config.read(locations):
        raise Exception('Could not find config file in any of: %s' % locations)
    return config
CONFIG = _load_configuration()
