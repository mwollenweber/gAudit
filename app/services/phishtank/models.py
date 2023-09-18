'''
services/alexa/models.py


Copyright Matthew Wollenweber 2014
mjw@cyberwart.com

'''

import sys
import traceback
from config import url, DEBUG
from datetime import datetime
from socket import inet_aton, inet_ntoa, gethostbyname_ex, gethostbyaddr, getfqdn, gaierror
from sqlalchemy.dialects.mysql import INTEGER, BLOB, DATETIME, TINYINT, TEXT
from urllib2 import urlopen, Request, URLError
from json import loads

from app.models import int2ip, ip2int
from sqlalchemy import ForeignKey, Integer, String, SmallInteger, Column

from app.database import db_session, Base


class phishTankModel(Base):
    __tablename__ = "phishTank"
    id = Column(INTEGER(unsigned=True), index=True, primary_key=True, autoincrement=False)
    url = Column(String(256), index=True)
    more_info = Column(String(256), index=True)
    submitted_td = Column(DATETIME, index=True, default=datetime.utcnow)
    verified_td = Column(DATETIME, index=True, default=datetime.utcnow)
    verified = Column(SmallInteger, default=0, index=True)
    online = Column(SmallInteger, default=0, index=True)
    ip = Column(INTEGER(unsigned=True), index=True, autoincrement=False)
    tdstamp = Column(DATETIME, index=True, default=datetime.utcnow)

    def insert(self, id, url, verified, online, ip_str, submitted_td, verified_td):
        self.id = int(id)
        self.url = str(url).strip()
        self.verified = verified
        self.online = online
        self.submitted_td = submitted_td

        if ip_str is not None:
            self.ip = ip2int(ip_str)

        if verified_td is not None:
            self.verified_td = verified_td

        self.tdstamp = datetime.utcnow()

        try:
            db_session.flush()
            db_session.merge(self)
            db_session.commit()

        except AttributeError:
            # traceback.print_exc(file=sys.stderr)
            meh = "meh"

        except:
            traceback.print_exc(file=sys.stderr)

    def update(self):
        print "Updating PhishTank database"
        data = self.fetch()
        dObject = loads(data)

        for phishDict in dObject:
            try:
                if phishDict.has_key("details"):
                    ip_str = phishDict['details'][0]['ip_address']

                else:
                    ip_str = None

                if phishDict['online'] == "yes":
                    online = True

                else:
                    online = False

                if phishDict['verified'] == "yes":
                    verified = True

                else:
                    verified = False

                phishID = phishDict['phish_id']
                submitted_td = phishDict["submission_time"]

                if phishDict.has_key("verification_time"):
                    verified_td = phishDict["verification_time"]

                else:
                    verified_td = None

                url = phishDict["url"]
                self.insert(phishID, url, verified, online, ip_str, submitted_td, verified_td)


            except AttributeError:
                traceback.print_exc(file=sys.stderr)
                continue

            except RuntimeError:
                traceback.print_exc(file=sys.stderr)
                continue
                # sys.exit(-1)

            except gaierror:
                traceback.print_exc(file=sys.stderr)
                continue

            except UnicodeEncodeError:
                traceback.print_exc(file=sys.stderr)
                print url
                continue

            except:
                traceback.print_exc(file=sys.stderr)
                continue

    def fetch(self):
        data = None

        try:
            req = Request(url)
            response = urlopen(req)
            data = response.read()

            return data

        except KeyboardInterrupt:
            traceback.print_exc(file=sys.stderr)
            sys.exit(0)

        except URLError:
            traceback.print_exc(file=sys.stderr)

        return data

    def isPhish(self, ip_str):
        target_ip = ip2int(ip_str)
        result = phishTankModel.query\
            .filter(target_ip >= phishTankModel.start)\
            .filter(target_ip <= et.end)\
            .first()

        if result:
            return True

        return False

    def isKnown(self, ip_str):
        return self.isPhish(self, ip_str)


if __name__ == "__main__":
    phishTank = phishTankModel()
    phishTank.update()
