import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def validate_passwords(self):
        if not (self.is_argument_present("password") and self.is_argument_present("confirm_password")):
            return False
        if not (self.get_argument("password") == self.get_argument("confirm_password")):
            return False
        return True
        
    def head(self, *args, **kwargs):
        self.get(*args, **kwargs)
        self.request.body = ''

    def get_secure_cookie(self, name, if_none=""):
        cook = tornado.web.RequestHandler.get_secure_cookie(self, name)
        if cook == None:
            return if_none
        return cook
        
    def get_current_user(self):
        return unicode(self.get_secure_cookie('login'))
        
    def is_argument_present(self, name):
        return not (self.request.arguments.get(name, None) == None)
        
    def send_errmsg(self, errmsg):
        self.set_secure_cookie("errmsg", errmsg)
        
    def send_statmsg(self, statmsg):
        self.set_secure_cookie("statmsg", statmsg)
        
    def render(self, template_name, **kwargs):
        #self.clear_all_cookies()
        error = self.get_secure_cookie("errmsg")
        status = self.get_secure_cookie("statmsg")
        self.clear_cookie("errmsg")
        self.clear_cookie("statmsg")
        #session.clear()
        tornado.web.RequestHandler.render(self,
                                          template_name,
                                          errmsg=error,
                                          statmsg=status,
                                          **kwargs)
