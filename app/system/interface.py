#-- MAIN APP -----------------------------------------------------------------
import os
import shutil
import sys
import argparse
import subprocess
import uuid

from app import __version__ as VERSION
from app.system.log import logger as _slk
from app.conf import TEMPLATE_THEME, PIDFILE_PATH
from app.system.interpreter import Interpreter

class RunApp(object):
    def __init__(self, sleekfmk_path):
        self.commons = dict()
        self.commons['top_dir'] = sleekfmk_path
        self.args = self.parse_options(sys.argv)
        self.logging_level = 10 if self.args.debug else ( 20 if self.args.verbose else 100 )
        _slk.setLevel(self.logging_level)
        self.commons['log'] = _slk

    def cmd_project(self, options):
        if options.runshell:
            shell = Interpreter('sleekfmk')
            shell.cmdloop()
        if options.rundebugshell:
            cmd = [ 'source %s && bpython' % (os.path.join(self.commons['top_dir'], 'env/bin/activate')) ]
            _slk.debug(cmd)
            subprocess.call(cmd, shell=True)
            return
        if options.runserver:
            from app.system import pid
            import daemon
            try:
                import tornado.httpserver
                import tornado.ioloop
                import tornado.options
                import tornado.web
            except ImportError:
                _slk.error("Cannot find tornado, needs installation.")
                sys.exit(1)
            _slk.info("Starting local tornado server %s:%s" % (options.server, options.port,))
            if not options.foreground:
                # check pidfile
                pidfile_path = PIDFILE_PATH
                try:
                    pid.check(pidfile_path)
                except IOError:
                    pass
                 
                # daemonize
                daemon_context = daemon.DaemonContext()
                with daemon_context:
                    # write the pidfile
                    pid.write(pidfile_path)
                 
                    # initialize the application
                    http_server = tornado.httpserver.HTTPServer(Application(self.commons['top_dir']))
                    http_server.listen(options.port)
                 
                    try:
                        # enter the Tornado IO loop
                        tornado.ioloop.IOLoop.instance().start()
                    finally:
                        # ensure we remove the pidfile
                        pid.remove(pidfile_path)
            else:
                # initialize the application
                http_server = tornado.httpserver.HTTPServer(Application(self.commons['top_dir']))
                http_server.listen(options.port)
                # enter the Tornado IO loop
                tornado.ioloop.IOLoop.instance().start()
        if options.host_template:
            from app.system.contrib.net import SetupHosts
            our_hosts = SetupHosts()
            _slk.debug(our_hosts)
            print "\n".join(our_hosts.run())
        if options.clean:
            _slk.info("Cleaning project")
        if options.update:
            _slk.info("Updating %s" % (" ".join(req_pkgs),))
            cmd = ['source env/bin/activate && pip install -U %s' % (" ".join(req_pkgs),)]
            subprocess.call(cmd, shell=True)
            _slk.info("Finished installing packages")
            
    def cmd_test(self, options):
        if options.runtest:
            import unittest
            from app.system.tests import discover_tests
            alltests = unittest.TestSuite([x for x in discover_tests(os.path.join(self.commons['top_dir'], 'app/system/tests'))])
            unittest.TextTestRunner(verbosity=2).run(alltests)

    def parse_options(self, *args, **kwds):
        parser = argparse.ArgumentParser(description='SleekFMK interface',
                                         prog='SleekFMK')
        subparsers = parser.add_subparsers()
        # Project commands
        projgroup = subparsers.add_parser("project", help="Project commands")

        projgroup.add_argument('--empty', action='store_true',
                            dest='dryrun', default=False,
                            help='Do not attempt to install required packages')
        projgroup.add_argument('--clean', action='store_true',
                            dest='clean', default=False,
                            help='Clean up project directory tree')
        projgroup.add_argument('--update', action='store_true',
                            dest='update', default=False,
                            help='Update or install required python packages')
        projgroup.add_argument('--shell', action='store_true',
                                     dest='runshell', default=False,
                                     help='Run project shell')
        projgroup.add_argument('--debugshell', action='store_true',
                                     dest='rundebugshell', default=False,
                                     help='Run project shell')
        projgroup.add_argument('--host-template', action='store_true',
                            dest='host_template', default=False,
                            help='Provide a general /etc/hosts template')
        projgroup.add_argument('--runserver', action='store_true', 
                            dest='runserver', default=False, help='Run test web server')
        projgroup.add_argument('--foreground', action='store_true', 
                            dest='foreground', default=False, help='Keep test server in foreground')
        projgroup.add_argument('--port', dest='port', default=10001,
                               help='Port in which server should run on')
        projgroup.add_argument('--server', dest='server', default="localhost",
                               help='Server hostname of application')
        projgroup.set_defaults(func=self.cmd_project)
        
        # Unittests
        test_sub = subparsers.add_parser("test", help="Run some tests")
        test_sub.add_argument('--all', dest='runtest',
                               action='store_true', default=False,
                               help='Run all unittests')
        test_sub.set_defaults(func=self.cmd_test)
        
        # Debug commands
        parser.add_argument('-d', '--debug', action='store_true',
                            dest='debug', default=False, help='show debug')
        parser.add_argument('-v', '--verbose', action='store_true',
                            dest='verbose', default=False, help='show info')
        parser.add_argument('--version', action='version',
                            version=VERSION,
                            help='Show version')
        return parser.parse_args()

    def run(self):
        self.args.func(self.args)

# preload views
from app.controllers import urls as controller_urls 
from app.api import urls as api_urls

urls = controller_urls.patterns + api_urls.patterns
import tornado.web
class Application(tornado.web.Application):

    def __init__(self, sleekfmk_path):
        settings = dict(
            template_path=os.path.join(sleekfmk_path, "app", "templates", TEMPLATE_THEME),
            static_path=os.path.join(sleekfmk_path, "app", "static", TEMPLATE_THEME),
            xsrf_cookies=True,
            cookie_secret='45d1d9ed94c34749a95960db2c68c652',
            login_url='/user/login',
            twitter_consumer_key="wdLsux7xmbjc7SWvQXjig",
            twitter_consumer_secret="K2h0iueJKGaU1V6oY5yeJIAW5wdMpRGvUu5sJRXbvrQ"
        )
        tornado.web.Application.__init__(self, urls, **settings)
