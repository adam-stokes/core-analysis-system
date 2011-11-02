#!/usr/bin/python
#  command
#  Overseer command for returning json data via RESTful calls
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

import sys
sys.path.append("/usr/share/cas")

if sys.version_info[:2] < (2,6):
    raise SystemExit("Python >= 2.6 required")

import os
import cherrypy
import simplejson
from caslib.db import *
from mako.template import Template
from mako.lookup import TemplateLookup
import subprocess
from multiprocessing import Process

current_dir = os.path.dirname(os.path.abspath(__file__))
mylookup = TemplateLookup(directories=[current_dir + '/static'])

def run(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return p

def gmap(obj):
    for item in obj.__dict__.items():
        if item[0][0] is '_':
            continue
        if isinstance(item[1], unicode):
            yield [item[0], str(item[1])]
        elif isinstance(item[1], datetime):
            # datetime objects aren't json iterable so we convert to time string
            yield [item[0], item[1].strftime("%I:%M%p %Y/%d/%m")]
        else:
            yield item

def json(obj):
    if isinstance(obj, list):
        return simplejson.dumps( map(lambda x: dict(x), map(lambda x: gmap(x), obj)) )
    else:
        return simplejson.dumps( dict(gmap(obj)) )

class Root:
    @cherrypy.expose
    def index(self):
        """ Ability to create/query jobs """
        session = Session()
        mytemplate = mylookup.get_template("index.html")
        latest_query = session.query(Job).order_by(Job.jobId.desc())[0:10]
        session.close()
        return mytemplate.render(recent=latest_query)

    @cherrypy.expose
    def create(self, **data):
        """ Create job """
        session = Session()
        if not session.query(Job).filter_by(identifier=data['identifier']).first():
            jobRecord = Job(data['identifier'],
                            data['email'],
                            data['vmcore'])
            session.add(jobRecord)
            session.commit()
            record = jobRecord
            cmd = "cas -i %s -f %s -e %s --job %s" % (record.identifier,
                                                      record.vmcore,
                                                      record.email,
                                                      record.jobId)
            # push cmd into background and let the cas application handle
            # any errors
            p = Process(target=run, args=(cmd,))
            p.start()
            p.join()
            if 'json' in data:
                return json(record)
            else:
                mytemplate = mylookup.get_template("create.html")
                return mytemplate.render(record=record)
        else:
            raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def status(self, **data):
        """ Return job stats """
        session = Session()
        status_query = session.query(Job).filter_by(jobId=data['id']).first()
        mytemplate = mylookup.get_template("status.html")
        session.close()

        # check for json output first
        if 'json' in data:
            return json(status_query)
        if status_query:
            return mytemplate.render(status=status_query)
        else:
            return mytemplate.render(errors={'error' : 'Job Not Found'})

    @cherrypy.expose
    def jobs(self, **data):
        """ list all jobs """
        session = Session()
        job_query = session.query(Job).order_by(Job.jobId.desc()).all()
        session.close()
        if 'json' in data:
            return json(job_query)
        else:
            mytemplate = mylookup.get_template("list.html")
            return mytemplate.render(job_query=job_query)

def main():
    root = Root()
    cherrypy.config.update(current_dir + "/site.conf")
    cherrypy.tree.mount(root, '/', current_dir + "/site.conf")
    cherrypy.engine.start()

if __name__=="__main__":
    main()
