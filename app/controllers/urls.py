import os
import tornado.web
from app.controllers.views import *
from app.system.contrib.auth import LogoutHandler
from app.conf import SLEEKAPP, TEMPLATE_THEME

static_serve = os.path.join(SLEEKAPP, "static", TEMPLATE_THEME)

patterns = [
    (r"/", Index),
    (r"/help/?", Help),
    # User authentication
    #(r"/user/login/?", Login),
    #(r"/user/logout/?", LogoutHandler),
    #(r"/user/register/?", Register),
    (r"/media/(.*)", tornado.web.StaticFileHandler, {"path" : static_serve}), 
]
