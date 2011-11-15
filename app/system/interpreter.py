import cmd
import os
from app.system.contrib.auth import hash_login
from app.conf import PIDFILE_PATH

class Interpreter(cmd.Cmd):
    def __init__(self, prompt):
        cmd.Cmd.__init__(self)
        self.prompt = prompt + '> '
        self.doc_header = 'Commands:'
        self.misc_header = 'Help topics:'
        self.undoc_header = ''

    def __get_pid(self):
        if os.path.isfile(PIDFILE_PATH):
            pid = open(PIDFILE_PATH, 'r').read()
            return pid
        else:
            print "Application server not running"
            return None

    def emptyline(self):
        # Don't do anything for an empty command
        pass

    def do_EOF(self, line):
        """Type Ctrl-D to exit the shell"""
        self.stdout.write('\n')
        # Exit the interpreter on ^D
        return True

    def cmdloop(self, *args, **kwargs):
        while True:
            try:
                cmd.Cmd.cmdloop(self, *args, **kwargs)
            except KeyboardInterrupt:
                self.stdout.write('\n')
                # Abort the current command and continue on ^C
                continue
            break

    def runscript(self, script):
        for line in script:
            if not line.strip().startswith('#'):
                self.onecmd(line)

    def help_help(self):
        # You've got to be kidding me
        self.stdout.write('Type "help <topic>" for help on commands\n')

    """ test
    def do_test(self, c):
       
        print 'Testing', ', '.join(c.split())

    def complete_test(self, text, line, begidx, endidx):
        params = ['foo', 'bar', 'baz', 'blarg', 'wibble']
        previous = frozenset(line.split())
        return [p for p in params if p not in previous and p.startswith(text)]
    """

    def do_login_hash(self, p):
        """login_hash (username) (password)"""
        try:
            username, password = p.split()
        except ValueError:
            print "just pass a username and password"
            return
        else:
            print "=> %s" % (hash_login(username, password),)

    def do_status(self, c):
        """Status of application server"""
        pid = self.__get_pid()
        if not pid:
            print "Server is not running"
        else:
            print "Server is running (%s)" % (pid,)

    def do_stop(self, c):
        """Stop server"""
        pid = self.__get_pid()
        if not pid:
            print "Server is not running"
        else:
            print "Stopping server at existing pid %s" % (pid,)
            output = os.popen("kill %s" % (pid,)).read()
            output = os.popen("./satin project --runserver")

    def do_start(self, c):
        """Start application server"""
        print "Starting server"
        pid = self.__get_pid()
        if pid:
            print "Server already started"
        else:
            output = os.popen("./satin project --runserver")
    
    def do_restart(self, c):
        """restarts application server"""
        pid = self.__get_pid()
        if pid:
            self.do_stop()
            self.do_start()
        else:
            self.do_start()

if __name__ == '__main__':
    shell = Interpreter('sleekfmk')
    shell.cmdloop()
