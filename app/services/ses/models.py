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


class sesModel(Base):
    __tablename__ = "ses"
    __table_args__ = {
        'extend_existing': True
    }

    id = Column(VARCHAR(32), index=True, primary_key=True)
    tdstamp = Column(DATETIME, index=True, default=datetime.utcnow)
    confidence = Column(SMALLINT(), default=0, index=True)
    severity = Column(SMALLINT(), default=0, index=True)
    description = Column(String(128), index=True)
    assessment = Column(String(128), index=True)
    restriction = Column(String(128), index=True)
    detectTime = Column(DATETIME, index=True)
    hostname = Column(String(128), index=True)

    #ip address/subnet
    start = Column(INTEGER(), index=True)
    end = Column(INTEGER(), index=True)
    domain = Column(String(128), index=True)
    url = Column(String(128), index=False)
    source = Column(String(128), index=True)

    def __init__(self, host=None, apikey=None):
        self.host = None
        self.apikey = None

        if host:
            self.host = host

        if apikey:
            self.apikey = apikey



    def insert(self, data):
        #keys = data.keys()
        for key, val in data.items():
            try:
                print "DEBUG: Inserting %s %s" % (key, val)
                self.key = val



                #db_session.flush()
                #db_session.merge(self)
                #db_session.commit()

            except:
                traceback.print_exc(file=sys.stdout)
                continue
