#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2014
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
    import pprint
    import time
    import traceback
    import threading
    import getpass
    import csv
    import gdata.apps.emailsettings.client

    from time import sleep
    from threading import Thread
    

except ImportError, e:
        from notify import *
        self._log.error('Failed to import the proper libraries')
        notify("Failed to import all libs",str(e),"INFO",True)


DEBUG = True

class ThreadedForwardDump:
    def __init__(self, admin_email, mydomain, passwd, infilename, outfilename = None, MAX_THREADS = 10):
        self.infile = open(infilename, "r")
        self.reader = csv.reader(self.infile, delimiter=',', quotechar='"')
        self.client = gdata.apps.emailsettings.client.EmailSettingsClient(domain=mydomain)
        self.client.ClientLogin(email=admin_email, password=passwd, source='your-apps')
        self.outfilename = outfilename
        self.outfile = None
        if outfilename != None:
            self.outfile = open(outfilename, "w")
        
        self.MAX_THREADS = MAX_THREADS
        self.thread_queue = []
        self.out_queue = []
        self.netid_queue = []        
        


    def getForwardTo(self, netid):
        try:
            netid = netid.strip()
            if len(netid) < 3: 
                return None
            
            resp = self.client.RetrieveForwarding(username = netid)
            elements = resp.get_elements()
            forwardTo = None
            for e in elements:
                attributes = e.extension_attributes
                values = attributes.values()
                if "forwardTo" in values:
                    forwardTo = attributes['value']
                    if len(forwardTo) > 4:
                        self.out_queue.append((netid, forwardTo))

        #except RequestError
        #should catch Google RequestErrors and sleep to throttle the limit
        
        except KeyboardInterrupt:
            sys.exit(-1)        
                        
        except:
            #pass
            traceback.print_exc() 
            
    def dumpForwards(self):
        print "Username,\tForwardingAddress"
        if self.outfile != None:
            self.outfile.write("Username,\tForwardingAddress\n")
        
        #prime the netid queue
        for row in self.reader:
            email = row[0].strip()
            netid = email[:email.find('@')]
            self.netid_queue.append(netid.strip())        
        
        #start the threads
        for i in range(0, self.MAX_THREADS -1):
            netid = self.netid_queue.pop()
            if netid != None:
                self.thread_queue.append(Thread(target=self.getForwardTo, args=(netid, )))
                self.thread_queue[i].start()
                
                
        #do work
        while len(self.netid_queue) > 0:
            for i in range(0, self.MAX_THREADS -1):
                alive = self.thread_queue[i].is_alive()
                if alive == False:
                    netid = self.netid_queue.pop()
                    self.thread_queue[i] = Thread(target=self.getForwardTo, args=(netid, ))
                    self.thread_queue[i].start()

            #dup below but I don't want to wait until everything is done before we get any results
            while len(self.out_queue) > 0:
                (netid, forwardTo) = self.out_queue.pop()
                print "%s,\t%s" % (netid, forwardTo)
                if self.outfile != None:
                    self.outfile.write("%s,\t%s\n" % (netid, forwardTo))
                    self.outfile.flush()
        
        
        #dup to above but we need to clear out the out queue before we leave              
        while len(self.out_queue) > 0:
            (netid, forwardTo) = self.out_queue.pop()
            print "%s,\t%s" % (netid, forwardTo)
            if self.outfile != None:
                self.outfile.write("%s,\t%s\n" % (netid, forwardTo))
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
    DEBUG = args.DEBUG
     
    try:
        admin = raw_input("Google Admin: ")
        mydomain = raw_input('domain: ')
        admin_email = admin + "@" + mydomain
        passwd = getpass.getpass("Password: ")
        
        if args.outfilename != None:
            tfd = ThreadedForwardDump(admin_email,mydomain , passwd, args.infilename, args.outfilename)
        
        else:
            tfd = ThreadedForwardDump(admin_email,mydomain , passwd, args.infilename)
        
        tfd.dumpForwards()
        
            
    except KeyboardInterrupt:
        sys.exit(-1)         
        
    except:
        traceback.print_exc() 


    
if __name__ == "__main__":
    main()
    
    