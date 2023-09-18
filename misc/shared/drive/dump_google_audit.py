#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2014
mjw@cyberwart.com
All Rights Reserved.


'''
__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@cyberwart.com'
__version__ = '0.1'
__date__ = '2012/09/22'


\
import os
import sys
import argparse
import pprint
import traceback
from apiclient import discovery
from apiclient.discovery import build
from oauth2client.client import *
from app.auth.models import User


from app.auth.models import User


class GoogleAuditService:
    def __init__(self, domain):
        myUser = User()
        gAuthJSON = myUser.refreshGoogleAuth(domain)

        credentials = Credentials.new_from_json(gAuthJSON)
        http = httplib2.Http()
        credentials.refresh(http)
        http = credentials.authorize(http)

        self.drive_service = discovery.build('drive', 'v2', http)

    def getUsersShares(self, username):
        query = ''' '%s' in writers  and shared is True''' % username
        results = self.drive_service.files().list(q=query).execute()
        return results


def main():
    gds = GoogleAuditService(domain="insomniac.technology")
    user_list = ["mjw", "gaudit"]
    print '''Username, "Title", createdDate, modifiedDate, kind, owners, editable'''
    for username in user_list:
        try:
            print gds.getUsersShares("mjw")
        
        except KeyboardInterrupt:
            sys.exit(-1)
            
        except:
            traceback.print_exc()        
            

if __name__ == "__main__":
    main()
    
