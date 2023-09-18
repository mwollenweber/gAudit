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


try:
    import os
    import sys
    import argparse
    import ConfigParser
    import csv
    import httplib2
    import json
    import MySQLdb
    import pprint
    import sqlite3
    import time
    import traceback
    import urllib2
    import urlparse
    from BeautifulSoup import BeautifulSoup
    import db
    
except ImportError, e:
        from notify import *
        self._log.error('Failed to import the proper libraries')
        notify("Failed to import all libs",str(e),"INFO",True)


DEBUG = True


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)
    
    args = parser.parse_args()
    DEBUG = args.DEBUG
    
    try:
        mydb = db.db()
        mydb.clean()
        
    except KeyboardInterrupt:
        sys.exit(-1)         
        
    except:
        traceback.print_exc() 

if __name__ == "__main__":
    main()
    
    