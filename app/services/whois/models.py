'''
services/whois/models.py

Copyright Matthew Wollenweber 2014
mjw@insomniac.technology




'''

import sys
import traceback
import threading
import time
import pprint

from ipwhois import IPWhois
from whois import extract_domain, whois, WhoisEntry
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER, DATETIME
from urllib2 import urlopen, Request, URLError
from io import BytesIO
from struct import unpack, pack
from sqlalchemy.exc import IntegrityError, InvalidRequestError, OperationalError
from sqlalchemy import Column, String

from app import DEBUG
from app.database import db_session, Base


class whoisModel(Base):
    __tablename__ = "whois"
    __table_args__ = {
        'extend_existing': True
    }

    #Domain should be larger, but limited by my cheap database instance
    domain = Column(String(128), index=True, primary_key=True)
    tdstamp = Column(DATETIME, index=True, default=datetime.utcnow)
    updated_date = Column(DATETIME, index=True)
    creation_date = Column(DATETIME, index=True)
    expiration_date = Column(DATETIME, index=True)
    city = Column(String(128), index=True)
    state = Column(String(16), index=True)
    country = Column(String(8), index=True)
    name = Column(String(128), index=True)
    email = Column(String(128), index=True)
    registrar = Column(String(128), index=True)
    ns1 = Column(String(128), index=True)
    ns2  = Column(String(128), index=True)
    ns3  = Column(String(128), index=True)
    ASN = Column(INTEGER, index=True)
    asn_start_addr = Column(INTEGER, index=True)
    asn_end_addr = Column(INTEGER, index=True)


    def __init__(self):
        print "meh"


    def lookupDomain(self, domain):
        return whois(domain)

    def lookupIP(self, IP):
        obj = IPWhois(IP)
        results = obj.lookup_rdap(depth=1)
        return results

    def insert(self, wDict):
        try:
            asn = wDict["asn"]
            netWhois = wDict["network"]

            for key, val in netWhois.items():
                if key is "country":
                    self.country = val

                elif key is "name":
                    self.name = val

            for k, v in wDict["objects"].items():
                print "obj = %s" % k

                for key, val in v.items():
                    if key is "contact":
                        pprint.pprint("contact: %s, %s" % (key, val))

                    elif key is "events":
                        events = val

                    elif key is "status":
                        status = val

                    #else:
                    #    pprint.pprint("unknown: %s, %s" % (key, val))
            #db_session.merge(self)
            #db_session.commit()

        except:
            traceback.print_exc(file=sys.stderr)
            sys.exit(-1)


if __name__ == "__main__":
    print "things!"
    wm = whoisModel()
    #print wm.lookupDomain("www.gwu.edu")
    #pprint.pprint(wm.lookupIP("128.164.1.16"))
    data = wm.lookupIP("128.164.1.16")
    wm.insert(data)

