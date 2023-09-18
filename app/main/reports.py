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


import sys
import argparse
import MySQLdb as mdb
import traceback


# local imports
from ..database import db


DEBUG = True


class gAuditReports():
    def __init__(self, mydb):
        if mydb is not None:
            self.mydb = mydb
            self.conn = mydb.get_con()
            self.cur = mydb.get_cur()

        else:
            print "ERROR: Invalid MySQL Connection"

    def reconnect(self):
        self.mydb.connect()
        self.cur = self.mydb.get_cur()
        self.conn = self.mydb.get_con()

    def listNigerians(self, authorizedDomain, start=None, end=None):
        results = []
        output = []

        query = ''' SELECT username, domain, tdstamp, INET_NTOA(ip)
                    FROM logins
                    WHERE ip BETWEEN INET_ATON('41.0.0.0') AND INET_ATON('41.255.255.255')
                    AND DATE(tdstamp) BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
                    AND domain = '%s'
                    GROUP BY username, domain, ip
                    ORDER BY tdstamp DESC, ip, username, domain''' % (authorizedDomain)

        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        for r in results:
            output.append(r)

        return output

    def searchCountryCode(self, code, authorizedDomain):
        results = []
        output = []

        if type(code) != str:
            return None

        if len(code) != 2:
            print "ERROR: invalid code length"
            return None

        query = '''SELECT username, domain, tdstamp, INET_NTOA(logins.ip), ip2country.code
                   FROM logins
                   JOIN ip2country ON logins.ip = ip2country.ip
                   WHERE ip2country.code = '%s'
                   AND domain = '%s'
                   ORDER by logins.tdstamp DESC, logins.username
                   LIMIT 1000''' % (code, authorizedDomain)

        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        for r in results:
            print r
            output.append(r)

        return output

    def searchIP(self, ip, authorizedDomain):
        results = []
        output = []

        if type(ip) != str:
            return None

        if len(ip) < 7 or len(ip) > 15:
            print "ERROR: invalid ip length"
            return None

        query = '''SELECT username, domain, tdstamp, INET_NTOA(logins.ip), ip2country.code
                   FROM logins
                   JOIN ip2country ON logins.ip = ip2country.ip
                   WHERE logins.ip = INET_ATON('%s')
                   AND domain = '%s'
                   ORDER by logins.tdstamp DESC, logins.username''' % (ip, authorizedDomain)

        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        for r in results:
            print r
            output.append(r)

        return output

    def searchNetID(self, netid, authorizedDomain):
        results = []
        output = []

        if type(netid) != str:
            return None

        if len(netid) < 3 or len(netid) > 20:
            print "ERROR: invalid netid"
            return None

        query = '''SELECT username, domain, tdstamp, INET_NTOA(logins.ip), ip2country.code
                   FROM logins
                   JOIN ip2country ON logins.ip = ip2country.ip
                   WHERE username = '%s'
                   AND domain = '%s'
                   ORDER BY logins.tdstamp DESC, logins.username''' % (netid, authorizedDomain)
        print query

        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        for r in results:
            print r
            output.append(r)

        return output

    def searchIPrange(self, start, end, authorizedDomain):
        results = []
        output = []

        if type(start) != str:
            return None

        if len(start) < 7 or len(start) > 15:
            print "ERROR: invalid ip length"
            return None

        if type(end) != str:
            return None

        if len(end) < 7 or len(end) > 15:
            print "ERROR: invalid ip length"
            return None

        query = '''SELECT username, domain, tdstamp, INET_NTOA(logins.ip), ip2country.code
                   FROM logins
                   JOIN ip2country ON logins.ip = ip2country.ip
                   WHERE logins.ip BETWEEN INET_ATON('%s') AND INET_ATON('%s')
                   AND logins.domain = '%s'
                   ORDER by logins.tdstamp DESC, logins.username''' % (start, end, authorizedDomain)

        try:
            print "DEBUG: query = %s " % query
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        for r in results:
            output.append(r)

        return output

    def mostDistinctCountries(self, authorizedDomain):
        results = []
        output = []

        query = '''SELECT username, domain, COUNT(DISTINCT(code)) as cnt
                   FROM user2country
                   WHERE domain LIKE '%s'
                   GROUP BY username, domain
                   ORDER BY cnt DESC , username, domain
                   limit 100''' % (authorizedDomain)

        try:
            print "DEBUG: query = %s " % query
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        for r in results:
            print r
            output.append(r)

        return output

    def mostActiveForeignIPs(self, authorizedDomain):
        results = []
        output = []

        query = '''
                SELECT INET_NTOA(logins.ip), ip2country.code, COUNT(DISTINCT(logins.username)) as count FROM logins
                JOIN ip2country ON logins.ip = ip2country.ip
                WHERE
                    DATE(tdstamp) BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
                    AND ip2country.code <> "US"
                    AND domain = '%s'
                GROUP BY logins.ip, domain
                ORDER BY count DESC, logins.ip''' % (authorizedDomain)

        try:
            print "DEBUG: query = %s " % query
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        for r in results:
            output.append(r)

        return output

    def mostActiveForeignCountries(self, authorizedDomain):
        results = []
        output = []

        query = ''' SELECT code, count(*) as cnt
                    FROM user2country
                      WHERE code <> 'US'
                      AND domain = '%s'
                    GROUP BY domain, code
                    ORDER BY cnt DESC
                    LIMIT 100''' % (authorizedDomain)

        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        except:
            traceback.print_exc()

        for r in results:
            output.append(r)

        return output

    def knownBad(self, authorizedDomain):
        results = []
        if authorizedDomain is None:
            return results

        query = '''SELECT username, domain, INET_NTOA(logins.ip)
                   FROM logins
                   RIGHT JOIN knownBad ON logins.ip = knownBad.ip
                   WHERE logins.domain = '%s'
                   GROUP BY username, domain, logins.ip
                   ORDER BY username
                   ''' % (authorizedDomain)


        try:
            self.cur.execute(query)
            results = self.cur.fetchall()

        except mdb.Error, e:
            self.reconnect()
            traceback.print_exc()

        return results


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)

    args = parser.parse_args()
    DEBUG = args.DEBUG

    try:
        pass

    except KeyboardInterrupt:
        sys.exit(-1)

    except:
        traceback.print_exc()

if __name__ == "__main__":
    main()