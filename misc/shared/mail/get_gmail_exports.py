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
__date__ = '2013/08/27'

try:
    import os
    import sys
    import argparse
    import ConfigParser
    import getpass
    import gnupg
    import hashlib
    import httplib2
    import json
    import logging
    import MySQLdb
    import pprint
    import sqlite3
    import time
    import timeit
    import traceback
    import urllib2
    import urlparse
    from gdata.apps.audit.service import *

except ImportError, e:
    print e
    sys.exit(-1)

DEBUG = True

# getAccountInformationRequestStatus(user, request_id)
#getAllAccountInformationRequestsStatus
#getAllMailboxExportRequestsStatus()
#getMailboxExportRequestStatus(user, request_id)


class EmailGrabber:
    def __init__(self, domain, username=None, passwd=None, path="./", verbose=True, gpgPath=None):
        print "I'm an email grabber"

        if username == None or passwd == None:
            self.username = getpass.getuser("Username: ")
            self.passwd = getpass.getpass("Password: ")

        else:
            self.username = username
            self.passwd = passwd

        self.audit_service = None
        self.client = None
        self.domain = domain
        self.path = path
        self.verbose = verbose
        self.gpgPath = gpgPath
        self.useGPG = False
        self.gpg = None

        self.createService()

    def printExportRequestSummary(self, filterDeleted=True):
        all_exports = self.audit_service.getAllMailboxExportRequestsStatus()
        print "Date Requested, Date Completed, Request ID, Target Email, Status, Requestor, Number of Files"
        for i in range(0, len(all_exports)):
            export_info = all_exports[i]
            status = export_info['status']
            if status.find("DELETED") == 0 and filterDeleted == True:
                continue

            adminEmailAddress = export_info['adminEmailAddress']
            userEmailAddress = export_info['userEmailAddress']
            requestId = export_info['requestId']
            requestDate = export_info['requestDate']

            if status.find("COMPLETED") == 0:
                completedDate = export_info['completedDate']
                numberOfFiles = int(export_info['numberOfFiles'])

            else:
                completedDate = ''
                numberOfFiles = -1

            print "%s, %s, %s, %s, %s, %s, %s" % (
            requestDate, completedDate, requestId, userEmailAddress, status, adminEmailAddress, numberOfFiles)


    def initGPG(self, gpgPath=None):
        self.gpg = gnupg.GPG(gnupghome=gpgPath)

    def decryptExport(self, fname):
        if self.gpg == None:
            self.initGPG()

        outname = fname[:-4]
        fHandle = open(fname, "rb")
        gpg.decrypt_file(f, passphrase=self.gpg_passwd, output=outname)
        fHandle.close()

        #hash the file
        #hashlib.sha256(data).hexdigest()

    def printExportRequestsByAdmin(self, admin, filterDeleted=False):
        all_exports = self.audit_service.getAllMailboxExportRequestsStatus()
        print "Date Requested, Date Completed, Request ID, Target Email, Status, Requestor, Number of Files"
        for i in range(0, len(all_exports)):
            export_info = all_exports[i]
            status = export_info['status']
            adminEmailAddress = export_info['adminEmailAddress']
            userEmailAddress = export_info['userEmailAddress']
            requestId = export_info['requestId']
            requestDate = export_info['requestDate']

            if status.find("DELETED") == 0 and filterDeleted == True:
                continue

            if adminEmailAddress.find(admin) != 0:
                continue

            if status.find("COMPLETED") == 0:
                completedDate = export_info['completedDate']
                numberOfFiles = int(export_info['numberOfFiles'])

            else:
                completedDate = ''
                numberOfFiles = -1

            print "%s, %s, %s, %s, %s, %s, %s" % (
            requestDate, completedDate, requestId, userEmailAddress, status, adminEmailAddress, numberOfFiles)


    def printExportRequestStatus(self, user, request_id):
        export_info = self.audit_service.getMailboxExportRequestStatus(user=user, request_id=request_id)
        status = export_info['status']

        adminEmailAddress = export_info['adminEmailAddress']
        userEmailAddress = export_info['userEmailAddress']
        requestId = export_info['requestId']
        requestDate = export_info['requestDate']

        #switch if status is 'COMPLETED' or not
        if status.find("COMPLETED") == 0:
            completedDate = export_info['completedDate']
            numberOfFiles = int(export_info['numberOfFiles'])

        else:
            completedDate = ''
            numberOfFiles = -1

        print "%s, %s, %s, %s, %s, %s, %s" % (
        requestDate, completedDate, requestId, userEmailAddress, status, adminEmailAddress, numberOfFiles)

    def printExportDownloadLinks(self, user, request_id):
        export_info = self.audit_service.getMailboxExportRequestStatus(user=user, request_id=request_id)
        status = export_info['status']
        if status.find("COMPLETED") == 0:
            numberOfFiles = int(export_info['numberOfFiles'])
            for i in range(0, numberOfFiles):
                key = "fileUrl" + str(i)
                file_url = export_info[key]
                print "%s, %s, %s, %s" % (request_id, user, str(i), file_url)

        else:
            print "Files unavailable"


    def isComplete(self, user, request_id):
        r = self.audit_service.getMailboxExportRequestStatus(user=user, request_id=request_id)
        if r['status'] == 'COMPLETED':
            return True
        else:
            return False

    def getAttachmentQuery(self):
        query = "has:attachment AND (filename:pdf OR filename:exe OR filename:jar OR filename:zip OR filename:rar OR filename:xls OR filename:doc OR filename:rtf OR filename:docx OR filename:xlsx)"
        return query

    def createService(self):
        audit_service = gdata.apps.audit.service.AuditService(domain=self.domain)
        client = audit_service.ClientLogin(self.username + "@" + self.domain, self.passwd)
        self.audit_service = audit_service
        self.client = client

    def createExportRequest(self, user, start=None, end=None, query=None):
        self.audit_service.createMailboxExportRequest(user=user, begin_date=start, end_date=end, include_deleted=True,
                                                      search_query=query)

    def printAllRequestForUser(self, user):
        print "fixme"

    def downloadExport(self, user, request_id, path="/Volumes/ramdisk/"):
        if self.isComplete(user=user, request_id=request_id) == False:
            print "Request is not ready"
            return False

        r = self.audit_service.getMailboxExportRequestStatus(user=user, request_id=request_id)
        numberOfFiles = int(r['numberOfFiles'])
        completedDate = r['completedDate']
        requestDate = r['requestDate']

        self.path = path

        for i in range(1, numberOfFiles + 1):
            key = "fileUrl" + str(i)
            url = r[key]
            response = urllib2.urlopen(url)
            data = response.read()

            outfileName = user + "_gmailExportFile" + str(i) + "of" + str(numberOfFiles) + ".mbox.gpg"
            print "writing to: %s%s" % (self.path, outfileName)
            f = open(self.path + outfileName, "wb")
            f.write(data)
            f.close()

            if self.verbose == True:
                print "Completed file %s of %s" % (i, numberOfFiles)


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)

    root = logging.getLogger()

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


if __name__ == "__main__":
    main()
    
    