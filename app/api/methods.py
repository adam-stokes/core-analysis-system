import json
import tornado.web

def return_json_response(handler, content):
    handler.set_header("Content-Type", "application/json")
    if ("callback" in handler.request.arguments):
        handler.write('%s(%s)' % (handler.get_argument('callback'), content))
    else:
        handler.write(content)

#-- PUBLIC METHODS --------------------------------------------------------

"""
class getUserRecord(tornado.web.RequestHandler):
    def get(self, api_version, name):
    return_json_response(self, json.dumps({"status":"yep it works!"}))
"""

class getApiIndex(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("Hello there and thanks for trying sleekfmk.")
