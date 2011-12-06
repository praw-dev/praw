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

import ConfigParser
import os
import sys


def _load_configuration():
    config = ConfigParser.RawConfigParser()
    module_dir = os.path.dirname(sys.modules[__name__].__file__)
    locations = [os.path.join(module_dir, 'reddit_api.cfg'),
                 os.path.expanduser('~/.reddit_api.cfg'),
                 'reddit_api.cfg']
    if not config.read(locations):
        raise Exception('Could not find config file in any of: %s' % locations)
    return config
CONFIG = _load_configuration()

# TODO: These shouldn't be hard coded but need to be until some decorators and
# helps are updated to not need them.
CACHE_TIMEOUT = CONFIG.getint('reddit', 'cache_timeout')
DEFAULT_CONTENT_LIMIT = CONFIG.getint('reddit', 'default_content_limit')
WAIT_BETWEEN_CALL_TIME = CONFIG.getint('reddit', 'wait_between_call_time')
