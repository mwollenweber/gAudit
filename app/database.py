#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2012
mjw@cyberwart.com
All Rights Reserved.

'''

__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@insomniac.technology'
__version__ = '0.0.1'
__date__ = '2013/11/30'

import sys
import os
import argparse
import ConfigParser
import MySQLdb as mdb
import traceback
import datetime
import config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from app import db as mydb

SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
DEBUG = True

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_size=32, max_overflow=128)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
db_session._model_changes = {}

Base = declarative_base()
Base.query = db_session.query_property()


class db():
    def __init__(self, config_file="./gaudit.cfg"):
        self.db = mydb
        self.Model = mydb.Model
        self.con = None
        self.cur = None
        self.username = None
        self.passwd = None
        self.database = None
        self.host = None
        self.config_file = config_file
        self.load_config()
        self.connect()
        self._model_changes = {}
        self.days_back = 30
        self.loginRetentionPeriod = 30
        self.correlationPeriod = 30
        self.Model

        if self.con is not None:
            print "Successfully Connected to %s" % self.host

        else:
            print "Houston there appears to be a problem"

    def load_config(self):
        try:
            config_file = self.config_file
            config = ConfigParser.ConfigParser()
            config.read(self.config_file)

            self.username = config.get('db', 'username')
            self.passwd = config.get('db', 'passwd')
            if len(self.passwd) < 3:
                self.passwd = os.environ.get('JAWSDB_PASSWD')

            if self.passwd is None:
                print "LOG: No Database password provided"

            self.host = config.get('db', 'host')
            self.database = config.get('db', 'database')

            # fixme
            self.days_back = config.get('gaudit', 'days_back')
            self.loginRetentionPeriod = config.get('gaudit', 'loginRetentionPeriod')
            self.correlationPeriod = config.get('gaudit', 'correlationPeriod')

        except:
            print "Using config file = %s" % self.config_file
            traceback.print_exc()
            sys.exit(-1)

    def connect(self):
        try:
            con = mdb.connect(self.host, self.username, self.passwd, self.database)
            cur = con.cursor()
            cur.execute("SELECT VERSION()")

            self.con = con
            self.cur = cur

        except mdb.Error, e:
            print "Using config file = %s" % self.config_file
            print "Host = %s\t Username = %s\t Password = %s\n" % (self.host, self.username, self.passwd)
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)

    def get_ver(self):
        try:
            self.cur.execute("SELECT VERSION()")
            ver = self.cur.fetchone()
            return ver

        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return "Unknown"

    def get_cur(self):
        if self.cur is not None:
            return self.cur
        else:
            self.connect()
            return self.cur

    def get_con(self):
        if self.con is not None:
            return self.con
        else:
            self.connect()
            return self.con

    def get_version(self):
        if self.cur is None:
            self.connect()

        self.cur.execute("SELECT VERSION()")
        ver = self.cur.fetchone()

        return ver

    def commit(self):
        if self.con is not None:
            self.commit()

        else:
            print "ERROR: Database connection lost. Reconnect before commit"

    def insertGeoIP(self, start, end, code, name):
        try:
            self.cur.execute(
                ''' REPLACE INTO geoip (start, end, code, name)
                    VALUES ('%s', '%s', '%s', '%s')''' % (start, end, code, name))

            self.con.commit()

        except mdb.OperationalError:
            traceback.print_exc()
            print "ERROR: Unknown. Trying to reconnect"
            self.connect()

        except:
            traceback.print_exc()

    def cleanET(self):
        try:
            query = ''' DELETE FROM etBlock WHERE DATE(tdstamp) < DATE_SUB(CURDATE(), INTERVAL 2 DAY)'''
            self.cur.execute(query)
            self.con.commit()

        except mdb.OperationalError:
            traceback.print_exc()
            print "ERROR: Unknown. Trying to reconnect"
            self.connect()

        except:
            traceback.print_exc()

    def insertMDL(self, ip, date=None, domain=None, url=None, comment=None):
        try:
            if date == None:
                date = str(datetime.datetime.now().isoformat())

            query = '''
                    REPLACE INTO mdlBlock(ip, comment, tdstamp)
                    VALUES (INET_ATON('%s'), "%s", '%s')
                    ''' % (ip, comment, date)

            self.cur.execute(query)
            self.con.commit()

        except mdb.OperationalError:
            traceback.print_exc()
            print "ERROR: Unknown. Trying to reconnect"
            self.connect()

        except:
            traceback.print_exc()

    def buildKnownBad(self):
        try:
            # correlate from ET
            print "LOG: Correlating ET with logins"
            query = '''
                    REPLACE INTO knownBad(
                    SELECT ip, "et" as source, logins.tdstamp, 50, 50
                          FROM logins JOIN et
                          WHERE ip BETWEEN et.start AND et.end)
                    '''

            self.cur.execute(query)
            self.con.commit()

            # correlate from MDL
            print "LOG: Correlating MDL with logins"
            query = '''
                    REPLACE INTO knownBad
                      (SELECT logins.ip, "MDL" as source, logins.tdstamp, 50, 50
                      FROM logins
                      JOIN mdlBlock ON logins.ip = mdlBlock.ip)
                    '''
            self.cur.execute(query)
            self.con.commit()

            print "LOG: Correlating phishTank with logins"
            query = '''
                    REPLACE INTO knownBad
                      (SELECT logins.ip, "phishTank" as source, logins.tdstamp, 50, 50
                      FROM logins
                      JOIN phishTank ON logins.ip = phishTank.ip)
                    '''
            self.cur.execute(query)
            self.con.commit()

            print "LOG: *** NEED TO CORRELATE ses ***"
            # correlate from X
            # query = '''
            #        '''
            # self.cur.execute(query)
            # self.con.commit()

        except mdb.OperationalError:
            traceback.print_exc()
            print "ERROR: Unknown. Trying to reconnect"
            self.connect()

        except:
            traceback.print_exc()

    def cleanKnownBad(self):
        try:
            query = '''DELETE FROM knownBad'''
            self.cur.execute(query)
            self.con.commit()

        except mdb.OperationalError:
            traceback.print_exc()
            print "ERROR: Unable to delete record. Try again"
            self.connect()

        except:
            traceback.print_exc()

    def getLastLogin(self, username):
        query = '''
                SELECT username, domain, INET_NTOA(ip), tdstamp
                FROM logins
                WHERE username LIKE "%s"
                ORDER BY tdstamp DESC limit 1;
                ''' % username

        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        return results

    def cleanLogins(self, domain='', period=None):
        # fix me
        loginRetentionPeriod = self.loginRetentionPeriod
        query = '''
                    DELETE FROM logins
                    WHERE DATE(tdstamp) NOT BETWEEN DATE_SUB(CURDATE(), INTERVAL '%s' DAY) AND CURDATE()
                    AND domain = '%s'
                ''' % (loginRetentionPeriod, domain)

        try:
            self.cur.execute(query)
            self.con.commit()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

    def cleanCountries(self, domain=''):
        try:
            query = ''' DELETE FROM ip2country'''
            self.cur.execute(query)

            query = ''' DELETE FROM user2country  WHERE domain = '%s' ''' % domain
            self.cur.execute(query)

            self.con.commit()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

    def clean(self):
        # fixme - must distinguish between server clean and client clean

        # self.cleanKnownBad()
        self.cleanLogins()
        self.cleanCountries()
        self.con.commit()


def init_db():
    import models
    import auth.models
    import app.models
    import app.services.phishtank.models
    import app.main.auditModel
    import app.auth.models
    import app.services.ses

    from app.auth import models
    from app.services.et import models
    from app.services.phishtank import models
    from app.services.alexa import models
    #from app.services.whois import models
    from app.services.mdl import models
    from app.services.ses import models
    from app import models

    print "LOG: Creating tables"
    Base.metadata.create_all(bind=engine)
    db_session.commit()


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)

    args = parser.parse_args()
    DEBUG = args.DEBUG

    try:
        init_db()

    except KeyboardInterrupt:
        sys.exit(-1)

    except:
        traceback.print_exc()


if __name__ == "__main__":
    main()
