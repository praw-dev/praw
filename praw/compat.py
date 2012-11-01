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
import sys
from six import MovedAttribute, add_move


# Define additional moves for the six import
add_move(MovedAttribute('HTTPError', 'urllib2', 'urllib.error'))
add_move(MovedAttribute('HTTPCookieProcessor', 'urllib2', 'urllib.request'))
add_move(MovedAttribute('Request', 'urllib2', 'urllib.request'))
add_move(MovedAttribute('URLError', 'urllib2', 'urllib.error'))
add_move(MovedAttribute('build_opener', 'urllib2', 'urllib.request'))
add_move(MovedAttribute('quote', 'urllib2', 'urllib.parse'))
add_move(MovedAttribute('urlencode', 'urllib', 'urllib.parse'))
add_move(MovedAttribute('urljoin', 'urlparse', 'urllib.parse'))


class CompatImporter(object):
    @classmethod
    def load_module(cls, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        module = fullname.rsplit('.', 1)[1]
        try:
            package = __import__('six.moves', fromlist=[module])
            mod = getattr(package, module)
            sys.modules[fullname] = mod
            return mod
        except ImportError:
            raise ImportError('No module named {0}'.format(fullname))

    def find_module(self, fullname, path=None):  # pylint: disable-msg=W0613
        if fullname.startswith('praw.compat'):
            return self
        return None


sys.meta_path.append(CompatImporter())
sys.modules['praw.compat'].__path__ = []
del CompatImporter
