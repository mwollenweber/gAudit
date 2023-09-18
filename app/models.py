'''
models.py


Copyright Matthew Wollenweber 2014
mjw@cyberwart.com

'''
import traceback
import sys
import pprint
import ConfigParser

from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import INTEGER, BLOB, DATETIME, TINYINT, TEXT, SMALLINT, VARCHAR
from sqlalchemy import Column, Integer, String
from socket import inet_aton, inet_ntoa
from struct import unpack, pack
from app.database import Base, db_session
from app import DEBUG
import app.database as db


def int2ip(addr):
    return inet_ntoa(pack("!I", addr))


def ip2int(addr):
    return unpack("!I", inet_aton(addr))[0]


class domainAccountInformationRequestModel(Base):
    __tablename__ = 'domainAccountInformationRequests'
    __table_args__ = {'extend_existing': True}
    emailAddress = Column(String(128), index=True)
    adminEmailAddress = Column(String(128), index=True)
    username = Column(String(128), index=True)
    domain = Column(String(64), index=True)
    status = Column(String(64), index=True)
    requestDate = Column(DATETIME(), index=True, default=datetime.utcnow)
    tdstamp = Column(DATETIME(), index=True, default=datetime.utcnow)
    completedDate = Column(DATETIME(), index=True, default=datetime.utcnow)
    numberOfFiles = Column(INTEGER(), default=0)
    requestID = Column(INTEGER(), primary_key=True, index=True)

    def __unicode__(self):
        return ""


class domainAccountModel(Base):
    __tablename__ = 'domainAccounts'
    __table_args__ = {'extend_existing': True}
    emailAddress = Column(String(128), primary_key=True, index=True)
    username = Column(String(128), index=True)
    domain = Column(String(64), index=True)
    fName = Column(String(32), index=True)
    lName = Column(String(32), index=True)
    isMailboxSetup = Column(SMALLINT(), default=1, index=True)
    isSuspended = Column(SMALLINT(), default=0, index=True)
    lastLogin = Column(DATETIME(), index=True, default=datetime.utcnow)
    recordUpdated = Column(DATETIME(), index=True, default=datetime.utcnow)

    def __unicode__(self):
        return ""

    def __init__(self, authorizedDomain='', current_user=None):
        self.authorizedDomain = authorizedDomain
        self.current_user = current_user

    def insert(self, approvedDomain, username, emailAddress, fName, lName, isMailBoxSetup, isSuspended, lastLogin):
        try:
            self.recordUpdated = datetime.utcnow()
            self.domain = str(approvedDomain).strip()
            self.username = str(username).strip()
            self.emailAddress = str(emailAddress).strip()
            self.fName = str(fName).strip()
            self.lName = str(lName).strip()
            self.isMailboxSetup = isMailBoxSetup
            self.isSuspended = isSuspended
            self.lastLogin = str(lastLogin).strip()

            db_session.merge(self)
            db_session.flush()
            db_session.commit()

        except AttributeError:
            traceback.print_exc(file=sys.stderr)

        except UnicodeEncodeError:
            traceback.print_exc(file=sys.stderr)

        except:
            traceback.print_exc(file=sys.stderr)

    def getAccountByUsername(self, current_user, targetUser):
        authorizedDomain = current_user.getAuthorizedDomains()[0]
        isAdmin = current_user.isAdmin()

        if isAdmin is True:
            print "is Admin!"
            results = domainAccountModel.query.filter(domainAccountModel.username == targetUser).all()

        else:
            print "Not admin. Searching differently"
            results = domainAccountModel.query \
                .filter(domainAccountModel.domain == authorizedDomain) \
                .filter(domainAccountModel.username == targetUser) \
                .all()

        response = []
        for result in results:
            response.append({
                "fName": result.fName,
                "lName": result.lName,
                "email": result.emailAddress,
                "isMailboxSetup": result.isMailboxSetup,
                "isSuspended": result.isSuspended,
                "lastLogin": result.lastLogin
            })

        return response

    def getNames(self, targetUser):
        response = [None, None]

        current_user = self.current_user
        if current_user is None:
            return response

        authorizedDomain = current_user.getAuthorizedDomains()[0]
        isAdmin = current_user.isAdmin()

        if isAdmin is True:
            results = domainAccountModel.query \
                .filter(domainAccountModel.username == targetUser) \
                .all()

        else:
            results = domainAccountModel.query \
                .filter(domainAccountModel.domain == authorizedDomain) \
                .filter(domainAccountModel.username == targetUser) \
                .all()

        if results is None:
            return response

        return [results[0].fName, results[0].lName]

    def getAccountByFamilyName(self, current_user, targetName):
        authorizedDomain = current_user.getAuthorizedDomains()[0]
        isAdmin = current_user.isAdmin()

        if isAdmin is True:
            results = domainAccountModel.query \
                .filter(domainAccountModel.lName == targetName) \
                .all()

        else:
            results = domainAccountModel.query \
                .filter(domainAccountModel.domain == authorizedDomain) \
                .filter(domainAccountModel.lName == targetName) \
                .all()

        response = []
        for result in results:
            response.append({"fName": result.fName,
                             "lName": result.lName,
                             "email": result.emailAddress,
                             "isMailboxSetup": result.isMailboxSetup,
                             "isSuspended": result.isSuspended,
                             "lastLogin": result.lastLogin})

        return response

    def listAccounts(self, current_user):
        authorizedDomain = current_user.getAuthorizedDomains()[0]
        isAdmin = current_user.isAdmin()

        results = domainAccountModel.query \
            .filter(domainAccountModel.domain == authorizedDomain) \
            .all()
        return results


class gDump():
    def __init__(self, service, config_file="./gaudit.cfg"):
        self.DEBUG = True
        self.config_file = config_file
        self.days_back = 30  # default, updated by config
        self.service = service
        self.load_config()
        self.mydb = db.db()

    def print_audit(self):
        audit = self.get_audit()
        for record in audit:
            email = record[0].strip()
            ipAddress = record[1].strip()
            timedate = record[2].strip()
            pprint.pprint("%s, %s, %s" % (email, ipAddress, timedate))

    def load_audit(self, recs):
        con = self.mydb.con
        cur = self.mydb.cur

        for r in recs:
            try:
                email = r[0].strip()
                (user, domain) = email.split('@')
                ip = r[1].strip()
                if ip.find(":") >= 0:
                    # ipv6 skipping
                    # fixme
                    continue

                tdstamp = r[2].strip()
                query = '''
                        REPLACE INTO logins
                        (username, domain, ip, tdstamp)
                        VALUES ('%s', '%s', INET_ATON('%s'), '%s')
                        ''' % (user, domain, ip, tdstamp)

                cur.execute(query)
                con.commit()

            except:
                print "ERROR: Unable to insert %s" % query
                continue

    def get_audit(self):
        total_count = 0
        service = self.service

        # figure out the start date for the audit
        today = datetime.utcnow()
        delta = timedelta(days=int(self.ingestPeriod))
        start = today - delta
        start = start.isoformat() + "Z"

        out = []
        req = service.activities().list(eventName=None, applicationName="login", userKey="all", actorIpAddress=None,
                                        startTime=start, maxResults=None, pageToken=None, filters=None, endTime=None)
        res = req.execute()
        while res is not None:
            item_count = 0
            for item in res['items']:
                try:
                    item_count += 1
                    email = item['actor']['email']
                    ipAddress = item['ipAddress']
                    timedate = item['id']['time']
                    # print out
                    out.append([email, ipAddress, timedate])

                except KeyError:
                    traceback.print_exc()
                    pprint.pprint("ERROR: issue with item = %s\n" % item)
                    continue

                except AttributeError:
                    traceback.print_exc()
                    pprint.pprint("ERROR: Appears we're out of entries. Bailing", sys.stderr)
                    sys.exit(-1)

                except IOError:
                    traceback.print_exc()
                    pprint.pprint("ERROR: IOError. Bailing", sys.stderr)
                    sys.exit(-1)

                except KeyboardInterrupt:
                    sys.exit(-1)

            # iterated through items in the last RESults
            try:
                total_count += item_count
                if total_count % 1000 == 0 and self.DEBUG is True:
                    pprint.pprint("Count = %s" % total_count)

                req = service.activities().list_next(req, res)
                if req is not None:
                    res = req.execute()

                else:
                    pprint.pprint("**** Looks Like We're Done *****")
                    res = None

            except KeyError:
                traceback.print_exc()
                pprint.pprint("ERROR: issue with item = %s\n" % item)

            except AttributeError:
                traceback.print_exc()
                pprint.pprint("ERROR: Appears we're out of entries. Bailing", sys.stderr)
                sys.exit(-1)

            except IOError:
                traceback.print_exc()
                pprint.pprint("ERROR: IOError. Bailing", sys.stderr)
                sys.exit(-1)

            except KeyboardInterrupt:
                sys.exit(-1)

            except client.AccessTokenRefreshError:
                print ("The credentials have been revoked or expired, please re-run"
                       "the application to re-authorize")
            except:
                traceback.print_exc()

        self.audit_data = out
        self.total_count = total_count
        return out

    def load_config(self):
        try:
            config_file = self.config_file
            config = ConfigParser.ConfigParser()
            config.read(self.config_file)

            # self.download_path = config.get('gaudit', 'download_path')
            # self.cache_path = config.get('gaudit', 'cache_path')
            # self.cache_file = config.get('gaudit', 'cache_file')
            self.ingestPeriod = config.get('gaudit', 'ingestPeriod')


        except:
            traceback.print_exc()
            sys.exit(-1)


if __name__ == "__main__":
    myAccount = domainAccountModel()
