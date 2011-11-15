import os

SITENAME = "cas"
SITELOGO = "logo_icon.jpg"
SITESLOGAN = "core analysis system"
SITEREV = "47b3a381698a"
# Top level absolute path of application
SLEEKAPP = os.path.abspath(os.path.dirname(__file__))

# Database credentials
dbhost = 'localhost'
dbport = '27017'        # default mongodb port
dbname = 'sleekdb1'

# Template theme
TEMPLATE_THEME="default"

# Additional required packages
more_req_pkgs = [
    # python-paramiko,
    # python-libxml2
]

PIDFILE_PATH='/var/run/cas.pid'
