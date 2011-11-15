# These may be overwritten through app/system/fixtures/
from app.system.handler import BaseHandler
from app.system.contrib.auth import LoginHandler, RegisterHandler
from app.system.contrib.html.head import add_metadata

meta = add_metadata("python, tornado, sleekfmk, web",
                "a python web application framework")
data = dict(meta=meta)

class Index(BaseHandler):
    def get(self):
        self.render("welcome.html", data=data)

class Help(BaseHandler):
    def get(self):
        self.render("help.html", data=data)
        
class Login(LoginHandler):
    def get(self):
        data['protector'] = self.xsrf_form_html()
        self.render("login.html", data=data)
        
class Register(RegisterHandler):
    def get(self):
        data['protector'] = self.xsrf_form_html()
        self.render("register.html", data=data)
