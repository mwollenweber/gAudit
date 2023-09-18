#!/usr/bin/python
'''

Copyright Matthew Wollenweber 2014
mjw@cyberwart.com
All Rights Reserved.

Reference: https://developers.google.com/admin-sdk/directory/v1/quickstart/quickstart-python



'''
__description__ = ''
__author__ = 'Matthew Wollenweber'
__email__ = 'mjw@cyberwart.com'
__version__ = '0.1'
__date__ = '2012/09/22'



import os
import sys
import argparse
import traceback
import httplib2
import time

from apiclient.discovery import build  
from oauth2client.client import *
from apiclient import errors
from oauth2client.client import OAuth2WebServerFlow

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    
    
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
	print "ERROR: update sample.dat"
	sys.exit(-1)
		#credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    directory_service = build('admin', 'directory_v1', http=http)

    all_users = []
    page_token = None
    params = {'customer': 'my_customer'}
    page = 0

    print "Queing Records"
    while True:
	if page > 0 and page % 100 == 0:
	    print "%s pages queued\n" % page

	try:
	    if page_token:
		params['pageToken'] = page_token
	    current_page = directory_service.users().list(**params).execute()
	    page += 1

	    all_users.extend(current_page['users'])

	    page_token = current_page.get('nextPageToken')
	    if not page_token:
		break

	except errors.HttpError as error:
	    print 'An error occurred: %s' % error
	    time.sleep(5)
	    continue




    #fix me
    print "Writing Records"
    user_count = 0
    f = open("/tmp/email.gwu.edu.csv", "w")  
    for user in all_users:
	if user_count > 0 and user_count % 100 == 0:
	    print "%s user records written" % user_count

	try:
	    user_count += 1
	    primaryEmail = isSuspended = givenName = familyName = lastLoginTime = creationTime = None

	    primaryEmail = user['primaryEmail']
	    isSuspended = user['suspended']
	    lastLoginTime = user['lastLoginTime']
	    creationTime = user['creationTime']    
	    givenName = user['name']['givenName']
	    familyName = user['name']['familyName']


	    f.write( "%s, %s, %s, %s, %s, %s\n" % (primaryEmail, familyName, givenName, isSuspended, lastLoginTime, creationTime))
	    f.flush()

	except KeyError:
	    traceback.print_exc()  
	    f.flush()
	    f.write( "%s, %s, %s, %s, %s, %s\n" % (primaryEmail, familyName, givenName, isSuspended, lastLoginTime, creationTime))

	except UnicodeEncodeError:
	    traceback.print_exc()
	    continue

	except KeyboardInterrupt:
	    traceback.print_exc()
	    sys.exit(-1)

	except:
	    traceback.print_exc()
	    print "exiting"
	    continue    

    f.close()
    print "Finished. Total User Records = %s" % user_count

if __name__ == "__main__":
    main()
	
	
