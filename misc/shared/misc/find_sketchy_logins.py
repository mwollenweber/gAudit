#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2012
mjw@cyberwart.com
All Rights Reserved.

Misc collection of audit features. Uses older API. Not ideal. 

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
    import httplib2
    import getpass
    import gnupg
    import json
    import pprint
    import re
    import sqlite3
    import StringIO
    import time
    import traceback
    import urllib2
    import urlparse
    from gdata.apps.audit.service import AuditService
    
except ImportError, e:
    print e
    sys.exit(-1)
    


DEBUG = True

class gSketchFinder:
    def __init__(self, domain, username = None, passwd = None):
        self.domain = domain
        self.aus = None
        self.gpg = None
        self.cache_path = None
        self.cache_file = None
        self.download_path = None
        self.request_list = []
        self.initGPG()
        self.load_config()
        
        if username == None or passwd == None:
            self.username = getpass.getuser("Google Admin Username: ")
            self.passwd = getpass.getpass("Google Admin Password: ")
            
        else:
            self.username = username
            self.passwd = passwd        
        
        
        try:
            aus = AuditService(domain=self.domain)
            aus.ClientLogin(username=self.username, password=self.passwd)
            if aus != None:
                self.aus = aus
        
        except KeyboardInterrupt:
            sys.exit(-1)        
                
        except:
            traceback.print_exc()   
            sys.exit(-1)           

    def createInfoRequestsFromList(self, target_list):
        ret = []
        for target in target_list:
            ret.append(self.createInfoRequest(target))
            
        return ret
    
    def createInfoRequestsFromFile(self, filename):
        target_list = []
        try:
            f = open(filename, "r")
            for line in f:
                line = line.strip()
                if line.find(self.domain) > 0:
                    line = line[0:line.find("@" + self.domain)]
                    
                target_list.append(line.strip())
                
        except KeyboardInterrupt:
            sys.exit(-1)
                
        except:
            traceback.print_exc()              
        
        return self.createInfoRequestsFromList(target_list)
    
    def createInfoRequest(self, target):
        try:
            resp = self.aus.createAccountInformationRequest(user=target)
            requestId = resp['requestId']
            userEmailAddress = resp['userEmailAddress']
        
            if True == True:
                print "created request %s for %s" % (userEmailAddress, requestId)
                
        except KeyboardInterrupt:
            sys.exit(-1)
            
        except:
            print "ERROR requesting info for %s" % target
            traceback.print_exc() 
            userEmailAddress = None
            requestId = None
            #sys.exit(-1)
            
        return (userEmailAddress, requestId)
        
    def listCompleteRequests(self):
        complete_audits = self.getCompleteRequests()
        for audit in complete_audits:
            print "%s, %s, %s" % (audit['userEmailAddress'], audit['requestId'], audit['completedDate'])
                
    def getCompleteRequests(self):
        complete_audits = []
        all_audits = self.aus.getAllAccountInformationRequestsStatus()
        for audit in all_audits:
            if audit['status'].find('COMPLETE') >= 0:
                complete_audits.append(audit)
                
        return complete_audits
        
    def getIncompleteRequests(self):
        print "incomplete"
        
    def listIncompleteRequests(self):
        print "incomplete requests"
        
        
    def downloadCompleteRequests(self, complete_audits = None, outfileName = None):
        ret = []
        if complete_audits == None:
            complete_audits = self.getCompleteRequests()
            
        if outfileName != None:
            try:
                out = open(outfileName, "a")
            except:
                traceback.print_exc() 
                out = sys.stdout
        else:
            out = sys.stdout
            
            
        for audit in complete_audits:
            if out != sys.stdout:
                out.close()
                out = open(outfileName, "a")
                
            username = audit['userEmailAddress']
            requestId = audit['requestId']
            
            #download the file
            nFiles = int(audit['numberOfFiles'].strip())
            if nFiles > 1: 
                print "WOW too many files n = %s" % nFiles
                 
            url = audit['fileUrl0']
            response = urllib2.urlopen(url)
            data = response.read()            
            

            clear_data_obj = self.gpg.decrypt(data, passphrase = self.gpg_passwd)
            #verify status is ok
            #print "decrypt status = %s" % clear_data_obj.status
            clear_data = clear_data_obj.data
            fakeFile = StringIO.StringIO(clear_data)
            
            regex = '^20[10-20].-[0-9]{1,2}.-[0-9]{1,2}\ [0-9]{1,2}:[0-9]{1,2}.*Log.*\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'
            r = re.compile(regex)
            
            for line in fakeFile:
                line = line.strip()
                
                if r.search(line) != None:
                    date = re.findall(r'^20[10-20].-[0-9]{1,2}.-[0-9]{1,2}', line)[0]
                    time = re.findall(r'[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}Z', line)[0]
                    ip = re.findall(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', line)[0]
                    #should probably get the event too
                    
                    #pprint.pprint("%s, %s, %s, %s, %s" % (username, requestId, date, time, ip), out)
                    dRecord = {"username":username, "requestId": requestId, "date":date, "time":time, "ip":ip}
                    pprint.pprint(dRecord)
                    
                    
                    ret.append((username, requestId, date, time, ip))
                else:
                    2+1
            
        if out != sys.stdout:
            out.close()
            
        return ret
            
    def initGPG(self, gpgPath = None):
        self.gpg = gnupg.GPG(gnupghome=gpgPath)
        self.gpg_passwd = getpass.getpass("GPG Passphrase: ")
        
    def decryptExport(self, fname):
        if self.gpg == None:
            self.initGPG()
              
        outname = fname[:-4]
        fHandle = open(fname, "rb")
        gpg.decrypt_file(f, passphrase=self.gpg_passwd, output=outname)
        fHandle.close()
        
    def load_config(self, config_file="./gaudit.cfg"):
        try:
            config_file = self.config_file
            config = ConfigParser.ConfigParser()
            config.read(self.config_file)
            
            self.download_path = config.get('gaudit', 'download_path')
            self.cache_path = config.get('gaudit', 'cache_path')
            self.cache_file = config.get('gaudit', 'cache_file')

            
        except:
            traceback.print_exc() 
            sys.exit(-1)
            



def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)
    parser.add_argument('--infile', '-i', type=str, dest='infilename', required=True)
    parser.add_argument('--domain', '-d', type=str, dest='domain', required=True)
    parser.add_argument('--user', '-u', type=str, dest='user', required=False)
    args = parser.parse_args()
    
    infileName = args.infilename
    username = args.username
    domain = args.domain
    
    
    gsf = gSketchFinder(domain, username, passwd)
    
    
    try:
        infile = open(infileName, "r")
        for netid in infile:
            print netid
            
    except KeyboardInterrupt:
        sys.exit(-1)  
        
    except:
        traceback.print_exc()   
        sys.exit(-1)
        


if __name__ == "__main__":
    main()
    