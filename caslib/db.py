#  cas-db library
#  Interface to CAS database
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

from datetime import datetime
# Mapper Object
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, backref
from sqlalchemy.orm import relation as relationship

Base = declarative_base()
class Core(Base):
    """ Corefile information """
    __tablename__ = 'cores'
    coreId = Column(Integer, primary_key=True)
    coreFile = Column(String(255))
    coreHash = Column(String(255))

    def __init__(self, coreFile, coreHash):
        self.coreFile = coreFile
        self.coreHash = coreHash

    def __repr__(self):
        return "<Core('%s','%s')>" % (self.coreFile, self.coreHash)

class Debug(Base):
    __tablename__ = 'debugs'
    debugId = Column(Integer, primary_key=True)
    debugPath = Column(String(255))
    
    def __init__(self, debugPath):
        self.debugPath = debugPath

    def __repr__(self):
        return "<Debug('%s')>" % (self.debugPath,)

class Job(Base):
    __tablename__ = 'jobs'
    jobId = Column(Integer, primary_key=True)
    identifier = Column(String(100))
    email = Column(String(40))
    vmcore = Column(String(255))
    path = Column(String(255))
    msg = Column(String(255))
    created = Column(DateTime, default=datetime.now)

    def __init__(self, identifier, email, vmcore, path=None, msg=None):
        self.identifier = identifier
        self.email = email
        self.vmcore = vmcore
        self.path = path
        self.msg = msg

    def __repr__(self):
        return "<Job('%s','%s','%s','%s','%s')>" % (self.identifier,
                                                    self.email,
                                                    self.vmcore,
                                                    self.path,
                                                    self.msg)
class Timestamp(Base):
    __tablename__ = 'timestamps'
    stampId = Column(Integer, primary_key=True)
    stampKey = Column(String(255))
    debugPath = Column(String(255))
    debugId = Column(Integer, ForeignKey("debugs.debugId"))

    debug = relationship(Debug, backref=backref('timestamps'))

    def __init__(self, stampKey, debugPath, debugId):
        self.stampKey = stampKey
        self.debugPath = debugPath
        self.debugId = debugId

    def __repr__(self):
        return "<Timestamp('%s','%s','%s')>" % (self.stampKey,
                                                self.debugPath,
                                                self.debugId)

class Server(Base):
    __tablename__ = 'servers'
    serverId = Column(Integer, primary_key=True)
    hostname = Column(String(100))
    port = Column(String(10))
    arch = Column(String(40))

    def __init__(self, hostname, port, arch):
        self.hostname = hostname
        self.port = port
        self.arch = arch

    def __repr__(self):
        return "<Server('%s','%s','%s')>" % (self.hostname,
                                             self.port,
                                             self.arch)

# Read cas.conf for database path
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("/etc/cas.conf")
try:
    dbpath = config.get('settings','database')
except:
    raise
engine = create_engine("sqlite:////%s" % (dbpath,))
Session = scoped_session(sessionmaker(bind=engine, autoflush=True))
Base.metadata.create_all(engine)
