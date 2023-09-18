#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2013
mjw@insomniac.technology
All Rights Reserved.

'''

__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@insomniac.technology'
__version__ = '0.0.1'
__date__ = '2013/11/30'

import os
import sys
import argparse
import traceback
import getpass
import csv

from apiclient.discovery import build
import gdata.apps.emailsettings.client
from oauth2client.client import Credentials

from threading import Thread
from app.auth.models import User
#from app import DEBUG
DEBUG = True

class ThreadedForwardDump:
    def __init__(self, mydomain, token, infilename, outfilename=None, MAX_THREADS=10):
        self.infile = open(infilename, "r")
        self.reader = csv.reader(self.infile, delimiter=',', quotechar='"')
        self.client = gdata.apps.emailsettings.client.EmailSettingsClient(domain=mydomain, auth_token=token)
        self.outfilename = outfilename
        self.outfile = None
        if outfilename != None:
            self.outfile = open(outfilename, "w")

        self.MAX_THREADS = MAX_THREADS
        self.thread_queue = []
        self.out_queue = []
        self.username_queue = []

    def getForwardTo(self, username):
        try:
            username = username.strip()
            if len(username) < 2:
                return None

            resp = self.client.RetrieveForwarding(username=username)
            elements = resp.get_elements()
            forwardTo = None
            for e in elements:
                attributes = e.extension_attributes
                values = attributes.values()
                if "forwardTo" in values:
                    forwardTo = attributes['value']
                    if len(forwardTo) > 4:
                        self.out_queue.append((username, forwardTo))

        #except RequestError
        #should catch Google RequestErrors and sleep to throttle the limit

        except KeyboardInterrupt:
            sys.exit(-1)


    def dumpForwards(self):
        outfile = self.outfile
        print "Username,\tForwardingAddress"
        if self.outfile is not None:
            self.outfile.write("Username,\tForwardingAddress\n")

        #prime the username queue
        for row in self.reader:
            email = row[0].strip()
            username = email[:email.find('@')]
            self.username_queue.append(username.strip())

        if len(self.username_queue) <= 0:
            print "ERROR no users in queue"
            sys.exit(-1)

        #start the threads
        for i in xrange(0, self.MAX_THREADS - 1):
            username = self.username_queue.pop()
            if username != None:
                self.thread_queue.append(Thread(target=self.getForwardTo, args=(username, )))
                self.thread_queue[i].start()

        #do work
        while len(self.username_queue) > 0:
            for i in range(0, self.MAX_THREADS - 1):
                alive = self.thread_queue[i].is_alive()
                if alive is False:
                    username = self.username_queue.pop()
                    self.thread_queue[i] = Thread(target=self.getForwardTo, args=(username, ))
                    self.thread_queue[i].start()

            #dup below but I don't want to wait until everything is done before we get any results
            while len(self.out_queue) > 0:
                (username, forwardTo) = self.out_queue.pop()
                print "%s,\t%s" % (username, forwardTo)
                if self.outfile is not None:
                    self.outfile.write("%s,\t%s\n" % (username, forwardTo))
                    self.outfile.flush()

        #dup to above but we need to clear out the out queue before we leave              
        while len(self.out_queue) > 0:
            (username, forwardTo) = self.out_queue.pop()
            print "%s,\t%s" % (username, forwardTo)
            if self.outfile is None:
                self.outfile.write("%s,\t%s\n" % (username, forwardTo))
                self.outfile.flush()

        self.infile.close()
        if outfile:
            self.outfile.close()


#https://developers.google.com/admin-sdk/email-settings/#retrieving_forwarding_settings
def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)
    parser.add_argument('--infile', '-i', type=str, dest='infilename', required=True)
    parser.add_argument('--outfile', '-o', type=str, dest='outfilename', required=False)

    args = parser.parse_args()

    try:

        mydomain = raw_input('domain: ')
        myUser = User()
        gAuthJSON = myUser.refreshGoogleAuth(mydomain)
        credentials = Credentials.new_from_json(gAuthJSON)


        if args.outfilename is not None:
            tfd = ThreadedForwardDump(mydomain, credentials, args.infilename, args.outfilename)

        else:
            tfd = ThreadedForwardDump(mydomain, credentials, args.infilename)

        tfd.dumpForwards()

    except KeyboardInterrupt:
        sys.exit(-1)

    except:
        traceback.print_exc()


if __name__ == "__main__":
    main()