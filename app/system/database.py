import os
import json
from app.system.contrib.util.loader import load_by_name
from app.conf import (dbhost,
                      dbname,
                      dbport)
from pymongo import Connection
from app.system.log import logger as _slk

db_collections = dict()

def db_init():
    try:
        connection = Connection(dbhost, int(dbport))
        return connection[dbname]
    except:
        return False
        
def load_collection(name):
    db = db_init()
    if not db:
        return None
    db_collections[name] = (db["%s_collection" % (name,)], db["%s" % (name,)])
    return db_collections[name][1]

def import_fixtures(commons):
    pass
