
import httplib2
import sys
import traceback
import urllib2
import gnupg
import io

import gdata.apps.audit.service
import locale
import time

from urllib2 import HTTPError
from functools import wraps


from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER, BLOB, DATETIME
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError
from apiclient.http import MediaUpload, MediaFileUpload
from apiclient.discovery import build
from apiclient import errors

from oauth2client import file

from app.auth.models import User
from app.database import db_session, engine, Base
from app.models import domainAccountModel
from app import db, DEBUG


class gpgModel(Base):
    __tablename__ = 'gpgKeys'
    __table_args__ = {
        'extend_existing': True
    }

    id = db.Column(Integer(), primary_key=True, autoincrement=True)
    domain = db.Column(String(64), index=True)
    tdstamp = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    owner = db.Column(String(128), index=True)
    keyRingName = db.Column(String(128), index=True)
    private = db.Column(BLOB())
    public = db.Column(BLOB())
    password = db.Column(BLOB())

    def __init__(self, domain, homedir="/home/mjw/GoogleAuditService/gpgHome"):
        self.gpg = None
        self.domain = domain
        self.gpgPath = None
        self.password = None
        self.public = None
        self.private = None
        self.homedir = homedir

        print "FIXME: should be more thoughtful about the gpg homedir"
        self.gpg = gnupg.GPG(homedir=self.homedir)
        self.gpg.encoding = locale.getpreferredencoding()


    def __unicode__(self):
        return ""

    def generateKey(self, domain, user):
        print "fixme"
        gpg = self.gpg
        #gpg.gen_key_input()

    def updateGPG(self, keydata):
        gpg = self.gpg
        gpg.import_keys(keydata)

        #fixme

    def decryptStream(self, data):
        gpg = self.gpg

        #fixme
        print "FIXME: auditModel::decryptStream password!!!"
        self.password = "gwu#$ediscovery42!"

        result = gpg.decrypt(data, passphrase=self.password)
        if result.status == 'decryption ok':
            output = result.data
            #print "decrypted length = %sM" % (len(output)/(8 * 1024))

        else:
            print "ERROR: Decryption Failed! gpg Status: %s" % result.status
            output = None

            #fixme: debug exiting early
            #print "ERROR: Dumping stream to /tmp/error.gpg"
            #f = open("/tmp/error.gpg", "w")
            #f.write(data)
            #f.close()
            sys.exit(-1)

        return output

    def insert(self, owner, private, public, password=None):
        self.owner = owner
        self.private = private
        self.password = password
        self.public = public

        try:
            self.tdstamp = datetime.utcnow()
            #db_session.flush()
            db_session.merge(self)
            db_session.commit()

        except IntegrityError:
            traceback.print_exc(file=sys.stderr)
            db_session.rollback()
            db_session.flush()

        except AttributeError:
            traceback.print_exc(file=sys.stderr)

        except:
            traceback.print_exc(file=sys.stderr)


class authorizationFiles(Base):
    '''
    Meh
    '''
    __tablename__ = 'authorizationFiles'
    __table_args__ = {
        'extend_existing': True
    }

    domain = db.Column(String(64), primary_key=True, index=True)
    createdBy = db.Column(String(64), primary_key=True, index=True)
    tdstamp = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    data = db.Column(BLOB(1024))

    def __init__(self, adminEmail, domain):
        print "fixme"
        #self.domain = current_user.getDomain()
        #self.createdBy = current_user.getEmail()
        self.domain = domain
        self.createdBy = adminEmail

        self.data = None

    def get(self):
        myself = self.query.filter(authorizationFiles.domain == self.domain)\
            .order_by(authorizationFiles.tdstamp.desc())\
            .first()

        return myself.data

    def update(self):
        print "fixme"

    def insert(self, data):
        self.data = data
        try:
            self.tdstamp = datetime.utcnow()
            db_session.flush()
            db_session.merge(self)
            #db_session.commit()

        except AttributeError:
            traceback.print_exc(file=sys.stderr)

        except IntegrityError:
            traceback.print_exc(file=sys.stderr)
            db_session.rollback()
            db_session.flush()

        except:
            traceback.print_exc(file=sys.stderr)


class availableAuditFilesModel(Base):
    '''
    model for available files. Basically just a table
    '''

    __tablename__ = 'availableAuditFiles'
    __table_args__ = {
        'extend_existing': True
    }


    requestID = db.Column(INTEGER(), ForeignKey("emailExportAudits.requestID"), primary_key=True)
    domain = db.Column(String(64), primary_key=True, index=True)
    fileNumber = db.Column(INTEGER(), primary_key=True, default=0)
    url = db.Column(String(512), index=False)
    tdstamp = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    downloadStatus = db.Column(INTEGER(), default=0)
    exportStatus = db.Column(INTEGER(), default=0)
    #fixme: needs a md5 db.Column
    #md5 = db.Column(String(32), index=False, default=0)


    def __init__(self, authorizedDomain):
        self.domain = authorizedDomain

    def __unicode__(self):
        return ""

    def setExportComplete(self, requestID):
        results = self.query.filter(availableAuditFilesModel.domain == self.domain)\
            .filter(availableAuditFilesModel.requestID == requestID)\
            .all()

        for res in results:
            res.exportStatus = 1
            db_session.merge(res)

        db_session.commit()

    def insert(self, requestID, fileNumber, url):
        self.requestID = requestID
        self.fileNumber = fileNumber
        self.url = url

        try:
            self.tdstamp = datetime.utcnow()
            db_session.merge(self)

        except AttributeError:
            traceback.print_exc(file=sys.stderr)

        except IntegrityError:
            traceback.print_exc(file=sys.stderr)
            db_session.rollback()
            db_session.flush()

        except:
            traceback.print_exc(file=sys.stderr)

    def listAvailableDownloads(self):
        results = self.query.filter(availableAuditFilesModel.domain == self.domain)\
            .filter(availableAuditFilesModel.downloadStatus == 0)\
            .all()

        out = []
        for result in results:
            out.append(result.requestID)

        return out

    def getDownloadURLs(self, requestID):
        results = self.query\
            .filter(availableAuditFilesModel.domain == self.domain)\
            .filter(availableAuditFilesModel.requestID == requestID)\
            .all()

        out = []
        for result in results:
            out.append(result.url)

        return out


    def listReadyFiles(self):
        print "fixme"


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

@retry(urllib2.URLError, tries=4, delay=3, backoff=2)
def urlopen_with_retry(url):
    return urllib2.urlopen(url)


class exportAudit(Base):
    '''
    Audit the exports

    '''
    __tablename__ = 'exportAudits'
    __table_args__ = {
        'extend_existing': True
    }

    id = db.Column(INTEGER(), primary_key=True, autoincrement=True)
    requestID = db.Column(INTEGER(), index=True)
    length = db.Column(INTEGER(), index=True, default=0)
    domain = db.Column(String(64), index=True)
    emailAddress = db.Column(String(128), index=True)
    adminEmailAddress = db.Column(String(128), index=True)
    fileNumber = db.Column(INTEGER(), default=0)
    decryptionStatus = db.Column(String(64), index=True)
    tdstamp = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    md5 = db.Column(String(128),  index=True)

    def __init__(self, authorizedDomain):
        self.domain = authorizedDomain


class emailExportAuditModel(Base):
    '''
    main model for email exports
    '''

    __tablename__ = 'emailExportAudits'
    __table_args__ = {
        'extend_existing': True
    }

    requestID = db.Column(INTEGER(), primary_key=True, index=True)
    domain = db.Column(String(64), primary_key=True, index=True)
    emailAddress = db.Column(String(128), index=True)
    adminEmailAddress = db.Column(String(128), index=True)
    username = db.Column(String(128), index=True)
    status = db.Column(String(32), index=True)
    contentType = db.Column(String(32), index=True)
    requestDate = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    beginDate = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    endDate = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    tdstamp = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    includeDeleted = db.Column(INTEGER(), default=0)
    completedDate = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    numberOfFiles = db.Column(INTEGER(), default=0)
    downloadStatus = db.Column(INTEGER(), default=0)
    exportStatus = db.Column(INTEGER(), default=0)
    gAuditUser = db.Column(String(128), index=True)
    #FIXME: folder url is needed
    #folderURL = db.Column(String(128), index=False, default=None)
    db.relationship('availableAuditFilesModel', backref="emailExportAudits", lazy='dynamic')

    def __init__(self, authorizedDomain, gAuditUser, current_user=None, GoogleDriveRootName="gAuditExports"):
        self.current_user = current_user
        self.domain = authorizedDomain
        self.gAuditUser = gAuditUser
        self.admin = None
        self.audit_service = None
        self.drive_service = None
        self.myGoogleDrive = None
        self.GoogleDriveRootName = GoogleDriveRootName

    def getGoogleService(self):
        gauth = User().getGoogleAuthByDomain(domain=self.domain)
        if gauth is None:
            print "ERROR: Unable to find google auth for domain=%s\nExiting!" % args.domain
            sys.exit(-1)

        credentials = file.Credentials().new_from_json(gauth)
        http = httplib2.Http()
        http = credentials.authorize(http)

        #print mydomain
        audit_service = gdata.apps.audit.service.AuditService(domain=self.domain)
        auth_headers = {u'Authorization': u'Bearer %s' % credentials.access_token}
        if DEBUG:
            print "Google Service auth_headers=%s" % auth_headers

        audit_service.additional_headers = auth_headers
        self.audit_service = audit_service

        return audit_service

    def __unicode__(self):
        return ""

    def commit(self):
        db_session.commit()

    def insert(self):
        print "fixme"

    def getNumberOfAvailableFiles(self, targetID):
        myAvailableFiles = availableAuditFilesModel(self.domain)
        myRequestID = int(targetID)
        print "mydomain = %s, my requestID = %s" % (self.domain, myRequestID)
        result_count = myAvailableFiles.query\
            .filter(availableAuditFilesModel.domain == self.domain)\
            .filter(availableAuditFilesModel.requestID == myRequestID)\
            .count()

        return result_count

    def getUsername(self, targetID):
        result = self.query\
            .filter(emailExportAuditModel.domain == self.domain)\
            .filter(emailExportAuditModel.requestID == int(targetID))\
            .first()

        if result is None:
            return None

        return str(result.emailAddress)

    def isComplete(self, user, request_id):
        if self.audit_service is None:
            self.getGoogleService()

        r = self.audit_service.getMailboxExportRequestStatus(user=user, request_id=request_id)
        if r['status'] == 'COMPLETED':
            return True

        else:
            return False

    def printExportRequestStatus(self, user, request_id):
        if self.audit_service is None:
            self.getGoogleService()

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

        print "%s, %s, %s, %s, %s, %s, %s" % (requestDate, completedDate, requestId, userEmailAddress, status,
                                              adminEmailAddress, numberOfFiles)

    def printAllExportRequestStatus(self):
        if self.audit_service is None:
            self.getGoogleService()

        audit_service = self.audit_service
        allExports = audit_service.getAllMailboxExportRequestsStatus()
        for export in allExports:
            status = export['status']

            adminEmailAddress = export['adminEmailAddress']
            userEmailAddress = export['userEmailAddress']
            requestId = export['requestId']
            requestDate = export['requestDate']

            #switch if status is 'COMPLETED' or not
            if status.find("COMPLETED") == 0:
                completedDate = export['completedDate']
                numberOfFiles = int(export['numberOfFiles'])

            else:
                completedDate = ''
                numberOfFiles = -1

            print "%s, %s, %s, %s, %s, %s, %s" % (requestDate, completedDate, requestId, userEmailAddress, status,
                                                  adminEmailAddress, numberOfFiles)

    def printExportDownloadLinks(self, user, request_id):
        if self.audit_service is None:
            self.getGoogleService()

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

    def fetchPartialMBOX(self, targetID, fileNumber):
        myFileDB = availableAuditFilesModel(self.domain)
        result = myFileDB.query\
            .filter(availableAuditFilesModel.domain == self.domain)\
            .filter(availableAuditFilesModel.requestID == int(targetID))\
            .filter(availableAuditFilesModel.fileNumber == int(fileNumber))\
            .first()

        fileNum = result.fileNumber
        url = result.url
        mbox = io.BytesIO()

        try:
            #FIXME: SPEED TEST
            data = "42 is the Answer, but what's the question?" #use this for speed
            eData = self.downloadFile(url)
            if eData is None:
                print "FIXME: Did not download audit file from google. My link was %s" % url
                return False

            data = self.decryptDataStream(eData)
            if data is None:
                print "FIXME: data did not decrypt"
                return False

            #(url, (len(data) / (8 * 1024)), md5(data).hexdigest())
            mbox.write(data)
            result.downloadStatus = 1
            db_session.merge(result)

        except KeyboardInterrupt:
            print "KeyboardInterrupt. Exiting"
            db_session.rollback()
            db_session.flush()
            sys.exit(0)

        except HTTPError:
            print "Exception downloading the file - setting status to 0. Rolling back and moving on."
            traceback.print_exc(file=sys.stderr)
            myFileDB.downloadStatus = 0
            self.downloadStatus = 0
            db_session.merge(self)
            db_session.commit()

        except IntegrityError:
            print "Exception downloading the file - setting status to 0. Rolling back and moving on."
            traceback.print_exc(file=sys.stderr)
            db_session.rollback()
            db_session.flush()

        except TypeError:
            print "Exception downloading the file - setting status to 0. Rolling back and moving on."
            traceback.print_exc(file=sys.stderr)
            db_session.rollback()
            db_session.flush()


        data = mbox.getvalue()
        mbox.close()

        db_session.merge(self)
        db_session.flush()
        return data

    def exportUserMailbox(self, targetUser, beginDate=None, endDate=None,
                          searchQuery=None, includeDeleted=True, headersOnly=False):
        if self.audit_service is None:
            self.getGoogleService()

        print self.audit_service.createMailboxExportRequest(user=targetUser,
                                                            begin_date=beginDate,
                                                            end_date=endDate,
                                                            search_query=searchQuery,
                                                            headers_only=headersOnly,
                                                            include_deleted=includeDeleted)
        self.updateAudits()

    def fetchMBOX(self, targetID):
        myFileDB = availableAuditFilesModel(self.domain)
        results = myFileDB.query\
            .filter(availableAuditFilesModel.domain == self.domain)\
            .filter(availableAuditFilesModel.requestID == int(targetID))\
            .all()

        downloads = []
        for result in results:
            fileNum = result.fileNumber
            url = result.url
            downloads.append([fileNum, url])

        mbox = io.BytesIO()
        downloads.sort(key=lambda tup: tup[0])
        for [i, url] in downloads:
            try:
                eData = self.downloadFile(url)
                data = self.decryptDataStream(eData)
                #(i, url, (len(data)/(8*1024)),md5(data).hexdigest())
                mbox.write(data)

            except KeyboardInterrupt:
                self.downloadStatus = 0
                db_session.merge(self)
                sys.exit(42)

            except HTTPError:
                traceback.print_exc(file=sys.stderr)
                self.downloadStatus = 0
                db_session.merge(self)
                db_session.commit()

            except IntegrityError:
                traceback.print_exc(file=sys.stderr)
                db_session.rollback()
                db_session.flush()

        data = mbox.getvalue()
        mbox.close()
        return data

    def downloadFile(self, url):
        data = []
        try:
            response = urlopen_with_retry(url)
            data = response.read()

        except HTTPError:
            traceback.print_exc(file=sys.stderr)

        except KeyboardInterrupt:
            print "KeyboardInterrupt! Exiting"
            sys.exit(0)

        return data

    def decryptDataStream(self, data):
        myGpg = gpgModel(self.domain)
        return myGpg.decryptStream(data)

    #fixme - that path isn't good for linux
    def downloadFilesToDisk(self, fileList, path="/Volumes/ramdisk/"):
        self.path = path
        numberOfFiles = len(fileList)
        for [i, url] in fileList:
            try:
                response = urllib2.urlopen(url)
                data = response.read()

                outfileName = self.domain + self.requestID + "File" + str(i) + "of" + str(numberOfFiles) + ".mbox.gpg"
                print "writing to: %s%s" % (self.path, outfileName)
                f = open(self.path + outfileName, "wb")
                f.write(data)
                f.close()

            except KeyboardInterrupt:
                print "KeyboardInterrupt! Exiting"
                sys.exit(0)

            except:
                traceback.print_exc(file=sys.stderr)

    def updateAudits(self):
        if self.audit_service is None:
            self.getGoogleService()

        audits = self.audit_service.getAllMailboxExportRequestsStatus()
        myFileDB = availableAuditFilesModel(self.domain)
        for audit in audits:
            #set these in GAS not via google to preserve the actual requestor
            self.gAuditUser = self.admin
            self.domain = self.domain
            self.downloadStatus = 0

            #get the values from Google's response
            self.adminEmailAddress = audit.get("adminEmailAddress")
            self.requestID = audit.get("requestId")
            self.status = audit.get("status")
            self.emailAddress = audit.get("userEmailAddress")
            self.beginDate = audit.get("beginDate")
            self.endDate = audit.get("endDate")
            self.completedDate = audit.get("completedDate")
            self.requestDate = audit.get("requestDate")
            self.contentType = audit.get("packageContent")
            self.searchQuery = audit.get("searchQuery")

            if audit.get("includeDeleted") is not "false":
                self.includeDeleted = 1

            else:
                self.includeDeleted = 0

            try:
                self.tdstamp = datetime.utcnow()
                db_session.merge(self)
                db_session.flush()

            except IntegrityError:
                traceback.print_exc(file=sys.stderr)
                db_session.rollback()
                #db_session.flush()

            except AttributeError:
                traceback.print_exc(file=sys.stderr)

            numFiles = audit.get("numberOfFiles")
            if numFiles is not None:
                self.numberOfFiles = int(numFiles)
                for i in range(0, self.numberOfFiles):
                    key = "fileUrl" + str(i)
                    url = audit.get(key)
                    myFileDB.insert(self.requestID, i, url)

                db_session.flush()

    def listAvailableDownloads(self):
        results = self.query\
            .filter(emailExportAuditModel.domain == self.domain)\
            .filter(emailExportAuditModel.status == "COMPLETED")\
            .all()

        out = []
        for result in results:
            out.append(result.requestID)

        return out

    def listCompleteAudits(self):
        results = self.query.filter(emailExportAuditModel.domain == self.domain)\
            .filter(emailExportAuditModel.status == "COMPLETED")\
            .all()
        return self.resultsAsDictionaryList(results)

    def listAudits(self):
        results = self.query.filter(emailExportAuditModel.domain == self.domain).all()
        return self.resultsAsDictionaryList(results)

    def listAuditsByAddress(self, targetAddress):
        results = self.query\
            .filter(emailExportAuditModel.domain == self.domain)\
            .filter(emailExportAuditModel.emailAddress == targetAddress)\
            .all()
        return self.resultsAsDictionaryList(results)

    def listAuditsByAdminAddress(self, adminAddress):
        results = self.query\
            .filter(emailExportAuditModel.domain == self.domain)\
            .filter(emailExportAuditModel.adminEmailAddress == adminAddress)\
            .all()
        return self.resultsAsDictionaryList(results)

    def listAuditDetails(self, requestID):
        print "DEBUG: Listing Audit details for audit %s in %s domain" % (requestID, self.domain)
        results = self.query\
            .filter(emailExportAuditModel.domain == self.domain)\
            .filter(emailExportAuditModel.requestID == requestID)\
            .all()
        return self.resultsAsDictionaryListDetailed(results)

    def lookupName(self, result):
        myDomainAccounts = domainAccountModel(current_user=self.current_user)
        offset = result.emailAddress.find("@")
        username = str(result.emailAddress)[:offset]
        return myDomainAccounts.getNames(username)

    def resultsAsDictionaryList(self, results):
        out = []
        for result in results:
            [first, last] = self.lookupName(result)
            out.append({
                "requestID": result.requestID,
                "requestor": result.adminEmailAddress,
                "emailAddress": result.emailAddress,
                "requestDate": result.requestDate,
                "status": result.status,
                "beginDate": result.beginDate,
                "endDate": result.endDate,
                "contentType": result.contentType,
                "includeDeleted": result.includeDeleted,
                "completedDate": result.completedDate,
                "fName": first,
                "lName": last
            })
        return out

    def getGoogleLinks(self, requestID):
        return availableAuditFilesModel(self.domain).getDownloadURLs(requestID)

    def resultsAsDictionaryListDetailed(self, results):
        out = []
        for result in results:
            [first, last] = self.lookupName(result)
            myFiles = availableAuditFilesModel(self.domain).getDownloadURLs(result.requestID)
            out.append({
                "NumberOfFiles": len(myFiles),
                "GoogleURLs": myFiles,
                "requestID": result.requestID,
                "requestor": result.adminEmailAddress,
                "emailAddress": result.emailAddress,
                "requestDate": result.requestDate,
                "status": result.status,
                "beginDate": result.beginDate,
                "endDate": result.endDate,
                "contentType": result.contentType,
                "includeDeleted": result.includeDeleted,
                "completedDate": result.completedDate,
                "fName": first,
                "lName": last,
                "StorageURL": "TBD"
            })

        return out

    def exportFilesToGoogle(self, requestID, rootID=None):
        if self.myGoogleDrive is None:
            myGoogleDrive = gDrive(domain=self.domain)
            self.drive_service = myGoogleDrive.service
            self.myGoogleDrive = myGoogleDrive

        else:
            myGoogleDrive = self.myGoogleDrive

        rootID = myGoogleDrive.getFolderIDfromTitle(self.GoogleDriveRootName)
        myParent = rootID
        folderLink = None
        targetAddress = self.getUsername(requestID)
        numberOfFiles = int(self.getNumberOfAvailableFiles(requestID))
        for fNumber in xrange(0, numberOfFiles):
            try:
                print "DEBUG: Exporting request=%s, file=%s" % (requestID, fNumber)
                data = self.fetchPartialMBOX(requestID, fNumber)
                if fNumber == 0 and data is not None:
                    myParent = myGoogleDrive.createFolder(folderName=requestID, parentID=rootID)
                    folderLink = myGoogleDrive.service.files().get(fileId=myParent).execute()["alternateLink"]

                if data is not None:
                    strNum = str(fNumber + 1)
                    #fixme - I hate actually writing to file
                    f = open("/tmp/out.mbox", "w")
                    f.write(data)
                    f.close()

                    myTitle = "Request_%s_File%s_of_%s_USER_%s.mbox" % (requestID, strNum, numberOfFiles, targetAddress)
                    mytype = "application/mbox"
                    myDescription = "Mailbox Export RequestID %s File %s For User %s" % (requestID, strNum, targetAddress)
                    myGoogleDrive.uploadFile(title=myTitle, filename="/tmp/out.mbox", description=myDescription,
                                             mime_type=mytype, parent_id=myParent)

                    # resource = service.files().insert(
                    # body=resource,
                    # media_body=MediaInMemoryUpload(
                    #     data.get('content', ''),
                    #     data['mimeType'],
                    #     resumable=True)
                    #     ).execute()

                    self.downloadStatus = 1
                    self.exportStatus = 1
                    db_session.merge(self)
                    db_session.flush()

            except IntegrityError:
                traceback.print_exc(file=sys.stderr)
                db_session.rollback()
                db_session.flush()
                return False

            except KeyboardInterrupt:
                print "KeyboardInterrupt! Exiting"
                db_session.rollback()
                db_session.flush()
                return False

        self.exportStatus = 1
        db_session.merge(self)
        db_session.flush()
        db_session.commit()

        print "FIXME: upload status/detail doc"
        print "DEBUG: gDrive Export of %s Complete. Available at: %s" % (requestID, folderLink)
        return True


class EmailMonitoringException(Exception):
    """Exception class for EmailMonitoring, shows appropriate error message."""


class EmailMonitoring(object):
    """Sample demonstrating how to perform CRUD operations on email monitor."""

    def __init__(self, consumer_key, consumer_secret, domain):
        """Create a new EmailMonitoring object configured for a domain.

        Args:
          consumer_key: A string representing a consumerKey.
          consumer_secret: A string representing a consumerSecret.
          domain: A string representing the domain to work on in the sample.
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.domain = domain
        self._Authorize()

    def _Authorize(self):
        """Asks the domain's admin to authorize access to the apps Apis."""
        self.service = AuditService(domain=self.domain, source='emailAuditSample')
        self.service.SetOAuthInputParameters(
            gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
            self.consumer_key, self.consumer_secret)
        request_token = self.service.FetchOAuthRequestToken()
        self.service.SetOAuthToken(request_token)
        auth_url = self.service.GenerateOAuthAuthorizationURL()
        print auth_url
        raw_input('Manually go to the above URL and authenticate.'
                  'Press Return after authorization.')
        self.service.UpgradeToOAuthAccessToken()

    def _CheckUsername(self, username):
        """Checks if a given username is valid or not.

        Args:
          username: A string to check for validity.

        Returns:
          True if username is valid, False otherwise.
        """
        if len(username) > 64:
            print 'Username length should be less than 64'
            return False
        pattern = re.compile('[^\w\.\+-_\']+')
        return not bool(pattern.search(username))

    def _GetValidUsername(self, typeof):
        """Takes a valid username as input.

        Args:
          typeof: A string representing the type of user.

        Returns:
          A valid string corresponding to username.
        """
        username = ''
        while not username:
            username = raw_input('Enter a valid %s username: ' % typeof)
            if not self._CheckUsername(username):
                print 'Invalid username'
                username = ''
        return username

    def _GetValidDate(self, is_neccessary):
        """Takes a valid date as input in 'yyyy-mm-dd HH:MM' format.

        Args:
          is_neccessary: A boolean denoting if a non empty value is needed.

        Returns:
          A valid string corresponding to date.
        """
        date = ''
        extra_stmt = ''
        if not is_neccessary:
            extra_stmt = '. Press enter to skip.'
        while not date:
            date = raw_input(
                'Enter a valid date as (yyyy-mm-dd HH:MM)%s:' % extra_stmt)
            if not (date and is_neccessary):
                return date
            try:
                datetime.strptime(date, '%Y-%m-%d %H:%M')
                return date
            except ValueError:
                print 'Not a valid date!'
                date = ''

    def _GetBool(self, name):
        """Takes a boolean value as input.

        Args:
          name: A string for which input is to be taken.

        Returns:
          A boolean for an entity represented by name.
        """
        choice = raw_input(
            'Enter your choice (t/f) for %s (defaults to False):' % name).strip()
        if choice == 't':
            return True
        return False

    def _CreateEmailMonitor(self):
        """Creates/Updates an email monitor."""
        src_user = self._GetValidUsername('source')
        dest_user = self._GetValidUsername('destination')
        end_date = self._GetValidDate(True)
        start_date = self._GetValidDate(False)
        incoming_headers = self._GetBool('incoming headers')
        outgoing_headers = self._GetBool('outgoing headers')
        drafts = self._GetBool('drafts')
        drafts_headers = False
        if drafts:
            drafts_headers = self._GetBool('drafts headers')
        chats = self._GetBool('chats')
        chats_headers = False
        if chats:
            self._GetBool('chats headers')
        self.service.createEmailMonitor(
            src_user, dest_user,
            end_date, start_date,
            incoming_headers, outgoing_headers,
            drafts, drafts_headers,
            chats, chats_headers)
        print 'Email monitor created/updated successfully!\n'

    def _RetrieveEmailMonitor(self):
        """Retrieves all email monitors for a user."""
        src_user = self._GetValidUsername('source')
        monitors = self.service.getEmailMonitors(src_user)
        for monitor in monitors:
            for key in monitor.keys():
                print '%s ----------- %s' % (key, monitor.get(key))
            print ''
        print 'Email monitors retrieved successfully!\n'

    def _DeleteEmailMonitor(self):
        """Deletes an email monitor."""
        src_user = self._GetValidUsername('source')
        dest_user = self._GetValidUsername('destination')
        self.service.deleteEmailMonitor(src_user, dest_user)
        print 'Email monitor deleted successfully!\n'

    def Run(self):
        """Handles the flow of the sample."""
        functions_list = [
            {
                'function': self._CreateEmailMonitor,
                'description': 'Create a email monitor for a domain user'
            },
            {
                'function': self._CreateEmailMonitor,
                'description': 'Update a email monitor for a domain user'
            },
            {
                'function': self._RetrieveEmailMonitor,
                'description': 'Retrieve all email monitors for a domain user'
            },
            {
                'function': self._DeleteEmailMonitor,
                'description': 'Delete a email monitor for a domain user'
            }
        ]

        while True:
            print 'What would you like to do? Choose an option:'
            print '0 - To exit'
            for i in range(0, len(functions_list)):
                print '%d - %s' % ((i + 1), functions_list[i].get('description'))
            choice = raw_input('Enter your choice: ').strip()
            if choice.isdigit():
                choice = int(choice)
            if choice == 0:
                break
            if choice < 0 or choice > len(functions_list):
                print 'Not a valid option!'
                continue
            try:
                functions_list[choice - 1].get('function')()
            except gdata.apps.service.AppsForYourDomainException, e:
                if e.error_code == 1301:
                    print '\nError: Invalid username!!\n'
                else:
                    raise e


class gDrive():
    def __init__(self, domain, flags=None):
        self.service = None
        self.parent_id = None

        gauth = User().getGoogleAuthByDomain(domain=domain)
        if gauth is None:
            print "ERROR: Unable to find google auth for domain=%s\nExiting!" % domain
            sys.exit(-1)

        credentials = file.Credentials().new_from_json(gauth)
        http = httplib2.Http()
        http = credentials.authorize(http)

        drive_service = build('drive', 'v2', http=http)
        self.service = drive_service

    def getFolderIDfromTitle(self, title):
        service = self.service
        query = '''title = '%s'  ''' % title
        results = service.files().list(q=query).execute()
        itemList = results['items']

        if itemList is not None:
            myFile = itemList[0]
            print "DEBUG: Found file by title. ID=%s" % myFile['id']
            return myFile['id']

        else:
            return None

    def retrieve_permissions(self, file_id):
        """Retrieve a list of permissions.

        Args:
          service: Drive API service instance.
          file_id: ID of the file to retrieve permissions for.
        Returns:
          List of permissions.
        """
        service = self.service

        try:
            permissions = service.permissions().list(fileId=file_id).execute()
            return permissions.get('items', [])

        except errors.HttpError, error:
            print 'An error occurred: %s' % error

        except KeyboardInterrupt:
            print "KeyboardInterrupt! Exiting"
            sys.exit(0)

        return None

    def update_permission(self, file_id, permission_id, new_role):
        """Update a permission's role.

        Args:
          service: Drive API service instance.
          file_id: ID of the file to update permission for.
          permission_id: ID of the permission to update. (USER ID)
          new_role: The value 'owner', 'writer' or 'reader'.

        Returns:
          The updated permission if successful, None otherwise.

        """

        service = self.service

        try:
            # First retrieve the permission from the API.
            permission = service.permissions().get(
                fileId=file_id, permissionId=permission_id).execute()
            permission['role'] = new_role
            return service.permissions().update(
                fileId=file_id, permissionId=permission_id, body=permission).execute()

        except errors.HttpError, error:
            print 'An error occurred: %s' % error

        except KeyboardInterrupt:
            print "KeyboardInterrupt! Exiting"
            sys.exit(0)

        return None

    def grantRead(self, file_id, emailAddress):
        return self.insert_permission(file_id, emailAddress, "user", "reader")

    def insert_permission(self, file_id, value, perm_type, role):
        """Insert a new permission.

        Args:
          service: Drive API service instance.
          file_id: ID of the file to insert permission for.
          value: User or group e-mail address, domain name or None for 'default'
                 type.
          perm_type: The value 'user', 'group', 'domain' or 'default'.
          role: The value 'owner', 'writer' or 'reader'.
        Returns:
          The inserted permission if successful, None otherwise.
        """
        service = self.service

        new_permission = {
            'value': value,
            'type': perm_type,
            'role': role
        }
        try:
            return service.permissions().insert(
                fileId=file_id, body=new_permission).execute()

        except errors.HttpError, error:
            print 'An error occurred: %s' % error

        except KeyboardInterrupt:
            print "KeyboardInterrupt! Exiting"
            sys.exit(0)


        return None

    def dump_share_info(self, username):
        google_username = username + self.domain
        drive_service = self.service

        query = ''' '%s' in readers''' % google_username
        results = drive_service.files().list(q=query).execute()
        items = results['items']
        for item in items:
            createdDate = item['createdDate']
            modifiedDate = item['modifiedDate']
            kind = item['kind']
            owners = item['ownerNames']
            title = item['title']
            editable = item['editable']
            print '''%s, "%s", %s, %s, %s, %s, %s''' % (
                username, title, createdDate, modifiedDate, kind, owners, editable)

    def uploadFile(self, filename, title=None, description=None, mime_type="application/octet-stream", parent_id=None):
        """Insert new file.

        Args:
          service: Drive API service instance.
          title: Title of the file to insert, including the extension.
          description: Description of the file to insert.
          parent_id: Parent folder's ID.
          mime_type: MIME type of the file to insert.
          filename: Filename of the file to insert.
        Returns:
          Inserted file metadata if successful, None otherwise.
        """
        service = self.service

        media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=False)
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]

        try:
            file = service.files().insert(body=body, media_body=media_body).execute()
            return file

        except errors.HttpError, error:
            print 'An error occured: %s' % error
            return None

        except KeyboardInterrupt:
            print "KeyboardInterrupt! Exiting"
            sys.exit(0)

    def getParentID(self):
        return self.parent_id

    def createFolder(self, folderName, parentID=None):
        # Create a folder on Drive, returns the newely created folders ID
        body = {
            'title': folderName,
            'mimeType': "application/vnd.google-apps.folder"
        }

        if parentID:
            body['parents'] = [{'id': parentID}]

        root_folder = self.service.files().insert(body=body).execute()
        folderID = root_folder['id']
        self.parent_id = folderID

        return folderID


class MediaInMemoryUpload(MediaUpload):
  """MediaUpload for a chunk of bytes.

  Construct a MediaFileUpload and pass as the media_body parameter of the
  method. For example, if we had a service that allowed plain text:
  """

  def __init__(self, body, mimetype='application/octet-stream',
               chunksize=256*1024, resumable=False):
    """Create a new MediaBytesUpload.

    Args:
      body: string, Bytes of body content.
      mimetype: string, Mime-type of the file or default of
        'application/octet-stream'.
      chunksize: int, File will be uploaded in chunks of this many bytes. Only
        used if resumable=True.
      resumable: bool, True if this is a resumable upload. False means upload
        in a single request.
    """
    self._body = body
    self._mimetype = mimetype
    self._resumable = resumable
    self._chunksize = chunksize

  def chunksize(self):
    """Chunk size for resumable uploads.

    Returns:
      Chunk size in bytes.
    """
    return self._chunksize

  def mimetype(self):
    """Mime type of the body.

    Returns:
      Mime type.
    """
    return self._mimetype

  def size(self):
    """Size of upload.

    Returns:
      Size of the body.
    """
    return len(self._body)

  def resumable(self):
    """Whether this upload is resumable.

    Returns:
      True if resumable upload or False.
    """
    return self._resumable

  def getbytes(self, begin, length):
    """Get bytes from the media.

    Args:
      begin: int, offset from beginning of file.
      length: int, number of bytes to read, starting at begin.

    Returns:
      A string of bytes read. May be shorter than length if EOF was reached
      first.
    """
    return self._body[begin:begin + length]


def main(argv):
    print "Don't run me"

if __name__ == '__main__':
    main(sys.argv)