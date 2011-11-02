#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import rpm
import os
import sys

if sys.version_info[:2] < (2,6):
    from caslib.cas_subprocess import Popen, PIPE, call
else:
    from subprocess import Popen, PIPE, call

def extractDebug(rpm, dst, tool="/usr/bin/rpm2cpio",
                 filter="*/vmlinux", return_results=True):
    """ extract file(s) from rpm
    """
    cpio = "/bin/cpio"
    cpio_args = "-imudv"
    filter_results = []
    # pipe to handle extraction, e.g. rpm2cpio \
    #     kernel.rpm | cpio -imud */vmlinux
    p1 = Popen([tool, rpm], stdout=PIPE)
    p2 = Popen([cpio,cpio_args,filter], stdin=p1.stdout,
        stdout=PIPE,stderr=PIPE)
    out, err = p2.communicate()
    if return_results:
        tmp = err.splitlines()[:-1]
        for item in tmp:
            filter_results.append(item)
        return filter_results
    return

