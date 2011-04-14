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

DEFAULT_CONTENT_LIMIT = 25
# Seconds to wait between calls, see http://code.reddit.com/wiki/API
# specifically "In general, and especially for crawlers, make fewer than one
# request per two seconds"
WAIT_BETWEEN_CALL_TIME = 2

CACHE_TIMEOUT = 30 # in seconds
