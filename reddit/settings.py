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
# How many results to retrieve by default when making content calls
import imp
import inspect
import os
import sys

# The domain to send API requests to. Useful to change for local reddit
# installations.
REDDIT_DOMAIN = 'www.reddit.com'

# The domain to use for SSL requests (login). Set to None to disable SSL
# requests.
HTTPS_DOMAIN = 'ssl.reddit.com'

DEFAULT_CONTENT_LIMIT = 25

# Seconds to wait between calls, see http://code.reddit.com/wiki/API
# specifically "In general, and especially for crawlers, make fewer than one
# request per two seconds"
WAIT_BETWEEN_CALL_TIME = 2

# Time, in seconds, to save the results of a get/post request.
CACHE_TIMEOUT = 30

# Mapping between RedditContent objects and their "kind" value. This is needed
# because these values differ between reddit installations.
OBJECT_KIND_MAPPING = {'Comment':      't1',
                       'Redditor':     't2',
                       'Submission':   't3',
                       'Subreddit':    't5',
                       'MoreComments': 'more'}

# Python magic to overwrite the above default values if a user-defined settings
# file is provided via the REDDIT_CONFIG environment variable.
if 'REDDIT_CONFIG' in os.environ:
    _tmp = imp.load_source('config', os.environ['REDDIT_CONFIG'])
    for name, _ in inspect.getmembers(sys.modules[__name__],
                                      lambda x: not inspect.ismodule(x)):
        if name.startswith('_'):
            continue
        if hasattr(_tmp, name):
            setattr(sys.modules[__name__], name, getattr(_tmp, name))
