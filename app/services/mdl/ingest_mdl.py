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


import traceback
import sys
import argparse
import csv
import ConfigParser
import urllib2
import StringIO
import app.database as db
from app import DEBUG


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)

    args = parser.parse_args()

    try:
        # fixme
        config_file = "server.cfg"
        config = ConfigParser.ConfigParser()
        config.read(config_file)

        blockURL = config.get('mdlBlock', 'file')
        response = urllib2.urlopen(blockURL)
        blockBuf = response.read()

    except:
        traceback.print_exc()
        sys.exit(-1)

    # connect to the database
    mydb = db.db(config_file="server.cfg")
    blockStream = StringIO.StringIO(blockBuf)

    reader = csv.reader(blockStream, delimiter=',', quotechar='"')
    for row in reader:
        try:
            datetime = row[0].strip()
            datetime = datetime.replace("_", " ")
            url = row[1].strip()
            ip = row[2].strip()

            #too short for an IP
            if len(ip) < 6:
                continue

                #too long for ip+cidr
            if len(ip) > 18:
                continue

            domain = row[3].strip()
            if len(domain) < 4:
                domain = None

            comment = row[4]
            contact = row[5]
            asn = row[6]

            if DEBUG is True:
                print "INSERTING %s, %s" % (ip, comment)

            mydb.insertMDL(ip=ip, comment=comment)

        except:
            traceback.print_exc()
            continue


if __name__ == "__main__":
    main()
