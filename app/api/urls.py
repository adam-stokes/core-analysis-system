import tornado.web
from app.api.methods import *

patterns = [
    (r"/api/([0-9]+)/?", getApiIndex),
#    (r"(/v/([0-9]+)/|/)user/([^/]{40})/?", getUserRecord),
]
