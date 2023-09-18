#!/usr/bin/python
__author__ = 'mjw'

import httplib2
import argparse
import traceback
import os
import sys
from apiclient import errors
from apiclient import discovery
from oauth2client import file

from app import DEBUG
from app.models import domainAccountModel
from app.auth.models import User


def main(argv):
    parser = argparse.ArgumentParser(description='Update the login events for a domain')
    parser.add_argument('--domain', type=str, required=True, help="You must specific the domain to update")
    args = parser.parse_args(argv)

    gdata = User().getGoogleAuthByDomain(domain=args.domain)
    if gdata is None:
        print "ERROR: Unable to find google auth for domain=%s\nExiting!" % args.domain
        sys.exit(-1)

    credentials = file.Credentials().new_from_json(gdata)
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Admin Reports API.
    directory_service = discovery.build('admin', 'directory_v1', http=http)

    all_users = []
    page_token = None
    params = {'customer': 'my_customer'}

    while True:
        try:
            if page_token:
                params['pageToken'] = page_token

            current_page = directory_service.users().list(**params).execute()
            all_users.extend(current_page['users'])
            page_token = current_page.get('nextPageToken')

            if not page_token:
                break

        except errors.HttpError as error:
            print 'An error occurred: %s' % error
            break

    for user in all_users:
        try:
            name = None
            givenName = None
            familyName = None
            isMailboxSetup = 1
            lastLogin = None
            isSuspended = 0

            myAccount = domainAccountModel()
            pos = user['primaryEmail'].find("@")
            approvedDomain = user['primaryEmail'][pos + 1:]
            username = user['primaryEmail'][:pos]

            if "name" in user:
                name = user['name']

            if 'givenName' in name:
                givenName = name['givenName']

            if 'familyName' in name:
                familyName = name['familyName']

            if 'isMailboxSetup' in user:
                if user['isMailboxSetup'] is True:
                    isMailboxSetup = 1

                else:
                    isMailboxSetup = 0

            if 'suspended' in user:
                if user['suspended'] is False:
                    isSuspended = 0

                else:
                    isSuspended = 1

            if 'lastLoginTime' in user:
                lastLoginTime = user['lastLoginTime']
                lastLogin = str(lastLoginTime).replace("Z", " ").replace("T", " ").strip()[0:-4]

            myAccount.insert(approvedDomain, username, user['primaryEmail'], givenName, familyName,
                             isMailboxSetup, isSuspended, lastLogin)

            if DEBUG:
                print "Inserting: %s, %s, %s, %s, %s, %s, %s, %s" % (
                    approvedDomain, username, user['primaryEmail'], givenName,
                    familyName, isMailboxSetup, isSuspended, lastLogin)

        except KeyboardInterrupt:
            sys.exit(0)

        except:
            traceback.print_exc(file=sys.stderr)



if __name__ == '__main__':
    main(sys.argv[1:])



