#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2012
mjw@cyberwart.com
All Rights Reserved.

'''
__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@cyberwart.com'
__version__ = '0.1'
__date__ = '2012/09/22'


try:
    import os
    import sys
    import argparse
    import ConfigParser
    import csv
    import httplib2
    import json
    import MySQLdb as mdb
    import pprint
    import sqlite3
    import time
    import traceback

    
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
    parser.add_argument('--infile', '-i', type=str, dest='infilename', required=False)

    args = parser.parse_args()
    infilename = args.infilename
    DEBUG = args.DEBUG
    
    if infilename == None:
        from dump_google_logins import gDump
        #FIX ME
        
    
    try:
        print "FIX ME"
        con = mdb.connect('localhost', 'gAudit', 'gwAudit', 'gAudit');
        cur = con.cursor()
        cur.execute("SELECT VERSION()")
        ver = cur.fetchone()
       
        with open(infilename, 'r') as gFile:
            reader = csv.reader(gFile)
            data = []
            for row in reader:
                data.append(row)
       
        #misc clean/prep        
        gFile.close()
        recs = []
        
        for x in data:
            email = x[0].strip()
            (user, domain) = email.split('@')
            ip = x[1].strip()
            td = x[2].strip()
            recs.append([user, domain,ip, td])
       
        for r in recs:
            try:
                email = r[0]
                domain = r[1]
                ip = r[2].strip()
                tdstamp = r[3]
                cur.execute("REPLACE INTO logins (username, domain, ip, tdstamp) VALUES ('%s', '%s', INET_ATON('%s'), '%s')" % (email, domain, ip, td))
            except:
                con.commit()
                continue       
        
        con.commit()
        
    except mdb.Error, e:    
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
        
    except KeyboardInterrupt:
        sys.exit(-1)         
        
    except:
        traceback.print_exc()     

    pprint.pprint("Done\n")

if __name__ == "__main__":
    main()
    
    