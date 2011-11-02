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
import os, sys

from caslib.util import Utility
from caslib import error_messages as _e

if sys.version_info[:2] < (2,6):
    from caslib.cas_subprocess import Popen, PIPE, call
    import caslib.cas_shutil as shutil
else:
    from subprocess import Popen, PIPE, call
    import shutil

# Pull in class methods from utility
util = Utility()

def casexecute(cmd, output=False):
    """ wrapper to subprocess for running external applications
    
    Arguments:
    - `cmd`: shell command to run
    - `output`: return std out
    """
    (stdout, stderr) = Popen(cmd,
                             shell=True,
                             bufsize=-1,
                             stdout=PIPE,
                             stderr=PIPE).communicate()
    if output:
        return stdout, stderr
    else:
        return

def coreFormat(data, fname):
    "Return a good default Operation, judging by the first 300 bytes or so."
    suffix_map = {  "tar" : ["tar", "xvf"],
                    "tgz" : ["tar", "xvzf"],
                    "gz"  : ["gunzip", "-q"],
                    "tbz" : ["tar", "xvjf"],
                    "bz2" : ["bunzip2", "-q"],
                    "zip" : ["unzip", "-f"]}

    # overwrite bz2 item if pbzip2 exists for use of multiple cores
    # during compression
    if os.path.isfile("/usr/bin/pbzip2"):
        suffix_map["bz2"] = ["pbzip2", "-d"]

    def string(offset, match):
        return data[offset:offset + len(match)] == match

    # Archives
    if string(257, 'ustar\0') or string(257, 'ustar\040\040\0'):
        return suffix_map["tar"]
    if string(0, 'PK\003\004'): return suffix_map["zip"]
    if string(0, 'PK00'): return suffix_map["zip"]

    # Compressed streams
    if string(0, '\037\213'):
        if fname.endswith('.tar.gz') or fname.endswith('.tgz'):
            return suffix_map["tgz"]
        return suffix_map["gz"]
    if string(0, 'BZh') or string(0, 'BZ'):
        if fname.endswith('.tar.bz') or fname.endswith('.tar.bz2') or \
           fname.endswith('.tbz') or fname.endswith('.tbz2'):
            return suffix_map["tbz"]
        return suffix_map["bz2"]
    return False

def coreExtract(filepath):
    """ utility to extract archive and pull out core
    """
    dst = os.path.dirname(filepath)
    fd = open(filepath, 'rb')
    data = os.read(fd.fileno(), 1000)
    format = coreFormat(data, filepath)
    if not format:
        return _e[5]
    else:
        format.append(filepath)
        p = Popen(format, stdout=PIPE, stderr=PIPE)
        err = p.stderr.read()
        out = p.stdout.read()
        if err:
            return False
        for root, dirs, files in util.directoryList(dst):
            for file in files:
                if coreIsCorefile(file):
                    return os.path.join(root,file)
        return _e[3]

def coreIsCorefile(corefile):
    cmd = ["file","-i",corefile]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    txt = p.stdout.read()
    items = ['application/x-coredump',
             'application/octet-stream',
             'application/x-executable']
    for i in items:
        if i in txt:
            return True
    return _e[6]

def coreTimestamp(path, blksize=None):
    """ captures fingerprint from core
    """
    match='Linux\sversion.*20\d{1,2}|#1\s.*20\d{1,2}'
    try:
        fd=open('%s' % (path))
    except IOError:
        return _e[7]
    fd.seek(0)
    if not blksize or blksize == "":
        blksize = 540000000
    b = os.read(fd.fileno(),blksize)
    out = util.regexSearch(match, b)
    fd.close()
    if out:
        return out
    return _e[4]

def coreCompress(corefile):
    """ use xz to do compression
    """
    if os.path.isfile("/usr/bin/xz"):
        cmd = "/bin/tar -c %s | /usr/bin/xz -1 > %s.xz" % (corefile,
                                                           corefile)
    else:
        cmd = "bzip2 -z %s" % (corefile,)
    out, err = casexecute(cmd, output=True)
    return out, err

def coreStrip(corefile, level=32):
    """ strip corefile with makedumpfile
    """
    pass
    
