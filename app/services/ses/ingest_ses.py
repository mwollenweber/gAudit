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


import os
import sys
import argparse
import ast

import csv
import httplib2
import json

import pprint

import time
import traceback
import urllib
import urllib2
import socket

import urlparse
from BeautifulSoup import BeautifulSoup

from app import DEBUG
from app.services.ses.models import sesModel
from config import SERVER, APIKEY

def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)

    args = parser.parse_args()

    socket.setdefaulttimeout(20)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent }
    baseURL = SERVER + "api?apikey=%s" % APIKEY

    ses = sesModel()

    queries = ["128.164.0.0/16", "domain/malware", "infrastructure/botnet", "domain/phishing"]
    queries = ["domain/malware", "domain/phishing"]
    for q in queries:
        try:
            url = baseURL + "&q=%s" % q
            print "Opening %s" %  url
            req = urllib2.Request(url, headers=headers)
            res = urllib2.urlopen(req)
            data = res.read()

            #data isn't json it's a list of dicts
            dictList = data.split('}')

            for d in dictList:
                if len(d) > 16:
                    data = d + "}"
                    data = data.replace(':null', ':"None"')
                    #pprint.pprint(data)
                    mydict = ast.literal_eval(data)
                    pprint.pprint(mydict)



        except ImportError:
            traceback.print_exc()
            continue




if __name__ == "__main__":
    main()
