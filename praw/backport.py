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

from six import MovedAttribute, add_move

add_move(MovedAttribute('HTTPError', 'urllib2', 'urllib.error'))
add_move(MovedAttribute('HTTPCookieProcessor', 'urllib2', 'urllib.request'))
add_move(MovedAttribute('Request', 'urllib2', 'urllib.request'))
add_move(MovedAttribute('URLError', 'urllib2', 'urllib.error'))
add_move(MovedAttribute('build_opener', 'urllib2', 'urllib.request'))
add_move(MovedAttribute('quote', 'urllib2', 'urllib.parse'))
add_move(MovedAttribute('urlencode', 'urllib', 'urllib.parse'))
add_move(MovedAttribute('urljoin', 'urlparse', 'urllib.parse'))
