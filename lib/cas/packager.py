#  packager.py
#  Packager Base
#  Copyright (C) 2012 Adam Stokes <hackr@cypherbook.com>
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

class Packager(object):
    _managers = {
        'RedHat' : {'manager':'/usr/bin/rpm','installer':'yum'},
        'Debian' : {'manager':'/usr/bin/dpkg', 'installer':'apt-get'}
        }
    
    def _test_packager(self):
        for k,v in self._managers.items():
            if os.path.isfile(v['manager']):
                return v
        return False

    def __get_item__(self):
        return self._test_packager()
    
    def __call__(self):
        return self._test_packager()
        
