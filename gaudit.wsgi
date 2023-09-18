#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(1, "../")
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")
sys.path.insert(1, "/usr/local/lib/python2.7/dist-packages/")
sys.path.insert(0, "/var/www/gAudit/app/")
sys.path.insert(0, "./")
sys.path.insert(0, "/var/www/gAudit/")

from app import create_app
application = create_app("development")
application.secret_key = 'Add your secret key'
