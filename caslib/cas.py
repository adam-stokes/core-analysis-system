#  cas.py
#  
#  Copyright (C) 2010 Adam Stokes
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" cas - core accessibility system.
"""
import sys
if sys.version_info[:2] < (2,4):
    raise SystemExit("Python >= 2.4 required")
try:
    from caslib.db import *
except:
    raise SystemExit('Can not interface with database, please check ' \
                     'configuration settings and try again')

# Main requirements honored; continue.
import optparse
import os
import ConfigParser
import smtplib
import socket
import paramiko
import hashlib
from urlgrabber import grabber
from subprocess import Popen, PIPE, call
import shutil

from datetime import datetime

from caslib.network import Executor, CasNetworkException
from caslib.core import coreTimestamp, coreExtract, coreIsCorefile, coreStrip
from caslib.util import Utility, genprint
from caslib.rpmutils import extractDebug
from caslib import error_messages as _e
from caslib import info_messages as _i

# Configuration parsing of /etc/cas.conf
# TODO: rework config read to place all items
#       into a key,value pair automatically
config = ConfigParser.ConfigParser()
config.read("/etc/cas.conf")
settings = {}
if config.has_section("settings"):
    for opt, val in config.items("settings"):
        settings[opt.upper()] = val

# Check for some advanced configurations
# Test to see if we provide a 32bit crash binary
# mainly used for x86_64 system who wish to analyze
# 32bit cores.
CRASH_32=None
if config.has_option("advanced", "crash_32"):
    CRASH_32=config.get("advanced", "crash_32")

# Do we have a buffersize
BUFFERSIZE=None
if config.has_option("advanced", "buffersize"):
    BUFFERSIZE=config.get("advanced", "buffersize")

def coreHandler(uri):
    try:
        downloadLocation = grabber.urlgrab(uri, filename=os.path.basename(uri), copy_local=1)
    except grabber.URLGrabError, e:
        return e
    if not coreIsCorefile(downloadLocation):
        corepath = coreExtract(downloadLocation)
        if not corepath:
            return False
        else:
            return corepath
    else:
        return downloadLocation

def timestampHandler(corefile):
    # dig through the buildstamp database and attempt to match it with
    # the one found in the core
    timestamp = coreTimestamp(corefile, BUFFERSIZE)
    if not coreTimestamp:
        raise SystemExit(err)
    # query timestamp table, return tuple debuginfoRPM, and path to
    # debugKernel
    sess = Session()
    timestamp_query = sess.query(Timestamp).filter(Timestamp.stampKey.like('%'+timestamp+'%')).first()
    if timestamp_query:
        return (timestamp_query)
    return _e[2]

class CasApplication(object):
    def __init__(self, args):
        self.parse_options(args)
        self.util = Utility()
        
    def parse_options(self, args):
        # build option - arguement list in the form of
        # cas -i <id> -f <filename> -e user@example.com
        parser = optparse.OptionParser(usage="cas [opts] args")
        parser.add_option("-i","--identifier", dest="identifier",
                          help="Unique ID for core")
        parser.add_option("-f","--file", dest="filename",
                          help="Filename")
        parser.add_option("-e","--email", dest="email",
                          help="Define email for results")
        parser.add_option("-m","--modules", dest="kernel_modules",
                          help="Extract associated kernel modules",
                          action="store_true")
        parser.add_option("--job", dest="job",
                          help="Define job id")
        parser.add_option("--compress", dest="compress_core",
                          help="Helper option to compress core to be transferred "\
                               "to another destination.", action="store_true")
        parser.add_option("--strip", dest="strip_core",
                          help="Strip out unecessary pages from core file",
                          action="store_true")

        self.opts, args = parser.parse_args()

        # filename _must_ exist
        if not self.opts.filename:
            parser.error("A file object is missing.")
        else:
            self.filename = os.path.abspath(self.opts.filename)

        # check if we want to strip the core
        if self.opts.strip_core:
            coreStrip(self.opts.filename)
            
        # check helper function first
        if self.opts.compress_core:
            out, err = coreCompress(os.path.abspath(self.opts.filename))
            if err:
                return _e[8]

        # we want to allow for multiple cores under same identifier
        # so we base the hierarchy /workDirectory/identifier/datetime
        datenow = datetime.now()
        dateFormatted = datenow.strftime("%Y.%m.%d.%I.%M.%S")

        # Not compressing lets continue with validating a identifier
        if not self.opts.identifier:
            parser.error("A unique identifier number is missing.")
        else:
            self.identifier = self.opts.identifier
            
        if not self.opts.email:
            parser.error("Email is missing")
        else:
            self.email = self.opts.email

        if not self.opts.job:
            parser.error("Job ID missing")

        self.extractKernelModules = self.opts.kernel_modules
        self.storagePath = os.path.join(settings["WORKDIRECTORY"],
                                        self.identifier)
        self.storagePath = os.path.join(self.storagePath, dateFormatted)

    def run(self):
        # Pull job data from db
        self.sess = Session()
        self.jobRecord = self.sess.query(Job).filter_by(jobId=self.opts.job).first()

        # setup directory structure
        self.jobRecord.msg = _i[1]
        self.sess.commit()
        if not os.path.isdir(self.storagePath):
            os.makedirs(self.storagePath)
            # Change to newly created directory to perform all tasks
            os.chdir(self.storagePath)
        self.jobRecord.msg = _i[2] + " : %s" % (self.storagePath,)
        self.sess.commit()
        # begin core extraction analysis
        corefile = coreHandler(self.filename)
        self.jobRecord.msg = _i[3] + ": %s" % (corefile,)
        timestamp = timestampHandler(corefile)
        self.jobRecord.msg = _i[5]
        self.sess.commit()
        if type(timestamp) == str:
            return False

        corefileArch = self.util.getElfArch(corefile)
        # Read current machine arch to see if we can bypass remote machine 
        # processing 
        currentMachineArch = Popen(["uname","-m"], stdout=PIPE, stderr=PIPE)
        currentMachineArch = currentMachineArch.stdout.read().strip()

        # check if an installed vmlinux can be used (symlink to save space)
        local_vmlinux = "/%s" % (timestamp.debugPath,)
        if currentMachineArch == corefileArch and \
               os.path.isfile(local_vmlinux):
            os.symlink(local_vmlinux, "%s/%s" % 
                         (self.storagePath, "vmlinux"))
            # define absolute path to debugkernel
            debugKernel = os.path.abspath("vmlinux")
        else:
            filterString = "*/%s" % (timestamp.debugPath,)
            extractDebug(timestamp.debug.debugPath, self.storagePath,
                         filter=filterString,
                         return_results=False)


        # setup crash file to finalize the processing of the core file
        self.util.buildCrashFile(self.storagePath, corefile, os.path.join('/',timestamp.debugPath))
        # Pull the architecture from the elf file to match up with a
        # server providing this architecture
        debugKernelArch = self.util.getElfArch(timestamp.debugPath)
        # Check if we have installed crash 32bit on system
        if debugKernelArch == "i686" and CRASH_32 is not None:
            import platform
            # Define current machine hostname, mainly used for email results.
            casProcessMachine = platform.uname()[1]
            # 32bit crash on same system.
            self.util.buildCrashFile(self.storagePath, corefile,
                                     timestamp.debugPath,
                                     crash_bin=CRASH_32)
            cmd = "./crash -i crash.in > crash.out"
            cmdPipe = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
            cmdData = cmdPipe.communicate()
            # pull status code to verify crash even ran to completeness
            sts, out, err = (cmdPipe.returncode, cmdData[0].strip(),
                             cmdData[1].strip())
            if sts:
                return (out, err)
        elif debugKernelArch == currentMachineArch:
            import platform
            # Define current machine hostname, mainly used for email results.
            casProcessMachine = platform.uname()[1]
            # The machine is suitable for processing the core through crash.
            cmd = "./crash -i crash.in > crash.out"
            cmdPipe = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
            cmdData = cmdPipe.communicate()
            # pull status code to verify crash even ran to completeness
            sts, out, err = (cmdPipe.returncode, cmdData[0].strip(),
                             cmdData[1].strip())
            if sts:
                self.jobRecord.msg = err
                self.sess.commit()
        else:
            # The machine running cas isn't capable of processing this core, lets
            # attempt with paramiko. Assuming paramiko is installed and a server database
            # is configured we attempt to process the core at another machine.
            try:
                serverList = self.sess.query(Server).all()
                ssh_obj = paramiko.SSHClient()
                ssh_obj.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
                if serverList:
                    for hostname, arch, port in serverList:
                        if arch == debugKernelArch:
                            # TODO: Randomize server selection
                            cmd = ["cd " + os.path.join(self.storagePath) + "\n",
                                   "./crash -i crash.in > crash.out\n"]
                            Executor(settings["SSHKEY"], hostname, 
                                     port, settings["CASUSER"],
                                     cmd).run()
                            break
                        else:
                            return False
                else:
                    self.jobRecord.msg = _e[80]
                    self.sess.commit()
                    return _e[80]
            except ImportError:
                return False
        crashOutFile = os.path.join(self.storagePath,"modules")
        if os.path.isfile(crashOutFile) and self.extractKernelModules:
            # Here we extract kernel modules processed from crash.out
            # this is usually desired during filesystem, storage
            # analysis of a core.
            crashOutFH = open(crashOutFile, 'r')
            crashOutData = crashOutFH.readlines()
            # search for MODULE NAME SIZE OBJECT FILE line
            for item in enumerate(crashOutData):
                idx, txt = item
                if 'MODULE' in txt:
                    index = idx
            moduleList = []
            # we have our index of above, now we obtain
            # the loaded modules from the list
            for item in crashOutData[index+1:]:
                moduleList.append(item.split()[1])
            # shift through moduleList extracting from
            # kernel as we go
            for module in moduleList:
                # This will extract all modules for each kernel within
                # the debuginfo.
                # TODO: Only extract the module for the debug kernel in use.
                moduleFilter = "*/"+module+".ko*"
                extractDebug(debuginfo, self.storagePath,
                             filter=moduleFilter,
                             return_results=False)
        # Just want to email the logfile to the submitter.
        crashOutFile = os.path.join(self.storagePath, "log")
        if os.path.isfile(crashOutFile) and \
               self.email and \
               settings["NOTIFY"]:
            try:
                mailServer = smtplib.SMTP(settings["SMTPHOST"])
                try:
                    # Compose email msg of results
                    msg = "Subject: CAS results for %s\r\n\n" % \
                          (self.identifier,)
                    msg += "Location: %s\n" % (self.storagePath,)
                    msg += "Server: %s\n" % (casProcessMachine,)
                    msg += "Output data:\n"
                    crashOutFH = open(crashOutFile,'r')
                    msg += crashOutFH.read()
                    crashOutFH.close()
                    #mailServer.set_debuglevel(0)
                    mailServer.sendmail(self.email,self.email,msg)
                finally:
                    mailServer.quit()
            except smtplib.SMTPException, e:
                self.jobRecord.msg = e
                self.sess.commit()
            except (os.error, socket.error), e:
                self.jobRecord.msg = e
                self.sess.commit()
                return False
        self.jobRecord.msg = _i[4]
        self.sess.commit()
        # cleanup job
        self.sess.close()
        return


