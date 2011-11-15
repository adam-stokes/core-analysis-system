import urllib
import base64
import traceback
from app.system.database import load_collection
from app.system.contrib.util.serialize import pkl_secure, pkl_decode
from app.system.handler import BaseHandler
from app.conf import dbhost, dbport

def hash_login(username, password):
    str_to_hash = "@@@@%s%s@@@@" % (username, password)
    b64encode = urllib.quote(base64.b64encode(str_to_hash).replace("/",".").replace("+","_").replace("=","-"))
    return b64encode

# Default authentication handlers
class LoginHandler(BaseHandler):
    def get(self):
        """ Override this method to provide a login form """
        pass
    
    def post(self):
        try:
            login_hash = hash_login(self.get_argument("username"),
                                    self.get_argument("password"))
            # load users collection
            users = load_collection('users')
            user = users.find_one({"login" : login_hash})
            if user.has_key('login'):
                self.set_secure_cookie("login", user['login'])
                self.send_statmsg("Successfully logged in.")
                self.redirect("/")
            else:
                self.send_errmsg("Login incorrect")
                self.redirect("/user/login")
        except:
            self.send_errmsg("Login incorrect")
            self.redirect("/user/login")
            
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("login")
        self.send_statmsg("Logged out successfully.")
        self.redirect("/")
        
class RegisterHandler(BaseHandler):
    def get(self):
        """ Override with register template """
        pass
    
    def post(self):
        """ Override with post template """
        try:
            if not (self.validate_passwords()):
                self.send_errmsg("Passwords empty/do not match")
                self.redirect("/user/register")
            login_hash = hash_login(self.get_argument("username"),
                                    self.get_argument("password"))
            # load users collection
            users = load_collection('users')
            if (users.find_one({"login" : login_hash})):
                self.send_errmsg("User exists")
                self.redirect("/user/register")
            user_attrs = dict(fullname=self.get_argument("fullname") or "john doe")
            app_attrs = dict()
            new_user = dict(login=login_hash,
                            login_attributes=pkl_secure(user_attrs, login_hash),
                            app_attributes=pkl_secure(app_attrs, login_hash),
                            rights=['normal_user'])
            users.insert(new_user)
            self.send_statmsg("Success!")
            self.redirect("/")
        except:
            self.send_errmsg("Registration failed: \n%s" % traceback.format_exc())
            self.redirect("/user/register")