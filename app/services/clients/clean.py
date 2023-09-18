#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2012
mjw@cyberwart.com
All Rights Reserved.

'''
__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@cyberwart.com'
__version__ = '0.0.1'
__date__ = '2013/11/30'


import sys
import argparse
import traceback

from oauth2client import file
from app import DEBUG
from app.auth.models import User
import app.database as db


def main(argv):
    parser = argparse.ArgumentParser(description='Update the login events for a domain')
    parser.add_argument('--domain', type=str, required=True, help="You must specific the domain to update")
    args = parser.parse_args(argv)

    gdata = User().getGoogleAuthByDomain(domain=args.domain)
    if gdata is None:
        print "ERROR: Unable to find google auth for domain=%s\nExiting!" % args.domain
        sys.exit(-1)

    credentials = file.Credentials().new_from_json(gdata)

    try:
        mydb = db.db()
        mydb.clean()
        
    except KeyboardInterrupt:
        sys.exit(-1)         
        
    except:
        traceback.print_exc() 

if __name__ == "__main__":
    main(sys.argv[1:])
