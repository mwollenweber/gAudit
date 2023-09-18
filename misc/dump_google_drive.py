#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2012
mjw@insomniac.technology
All Rights Reserved.

'''
__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@insomniac.technology'
__version__ = '0.1'
__date__ = '2012/09/22'



import os
import sys
import argparse
import pprint
import traceback
from apiclient import discovery
from apiclient.discovery import build
from oauth2client.client import *
from app.auth.models import User


class GoogleDriveService:
    def __init__(self, domain):
        self.domain = domain
        myUser = User()
        self.user = myUser

        gAuthJSON = myUser.getGoogleAuthByDomain(domain)
        credentials = Credentials.new_from_json(gAuthJSON)
        http = httplib2.Http()
        credentials.refresh(http)
        http = credentials.authorize(http)
        self.drive_service = discovery.build('drive', 'v2', http)


    def ListAllSharedFilesByUser(self, username):
        google_username = username + "@" + self.domain
        drive_service = self.drive_service

        query = ''' sharedWithMe  '''


        results = drive_service.files().list(q=query).execute()

        items = results['items']
        for item in items:
            createdDate = item['createdDate']
            modifiedDate = item['modifiedDate']
            kind = item['kind']

            title = item['title']
            #editable = item['editable']

            ownersStr = ""
            owners = item['ownerNames']
            for o in owners:
                ownersStr += str(o)

            sharingUser= item["sharingUser"]["emailAddress"]
            sharinguserStr = ""
            for su in sharingUser:
                sharinguserStr += str(su)


            pprint.pprint('''%s, "%s", %s''' % ( "title", "Owner", "Sharing Users"))
            pprint.pprint("%s Owners: %s    Sharing Users: %s\n" % (title, ownersStr, sharinguserStr))


def main():
    gds = GoogleDriveService(domain="insomniac.technology")
    user_list = ["mjw", "gaudit"]
    print '''Username, "Title", createdDate, modifiedDate, kind, owners, editable'''
    for username in user_list:
        try:
            username = username.strip()
            gds.ListAllSharedFilesByUser((username))


        except KeyboardInterrupt:
            sys.exit(-1)
            
        except:
            traceback.print_exc()        
            

if __name__ == "__main__":
    main()
    
