# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Admin Reports API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
import pprint
import traceback
import pymongo


from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/1060189277532/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/admin.reports.audit.readonly',
      'https://www.googleapis.com/auth/admin.reports.usage.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Admin Reports API.
  service = discovery.build('admin', 'reports_v1', http=http)

  #initialize mongo connection
  #client = pymongo.MongoClient('localhost', 2701)
  #db = client.GWlogin_db
  


  #good to go
  ip_list = []
  total_count = 0

  print "Success! Now add code here."
  start = "2013-09-29T00:00:00.000Z"
  start = None
  
  infileName = '/Volumes/ramdisk/ip_list.txt'
  f = open(infileName, 'r')
  for line in f:
    ip_list.append(line.strip())
  f.close()
  
  out = open("/Users/mjw/google_login_audit_ip.csv", "a")
  
  for ip in ip_list:
    pprint.pprint("Searching for IP = %s" % ip)
    req = service.activities().list(eventName = None, applicationName="login", userKey="all", actorIpAddress=ip, startTime=start, maxResults=None, pageToken=None, filters=None, endTime=None)
    res = req.execute()
    
    while res != None:
      item_count = 0
      #if res.has_key("items") == False:
       # continue      

      for item in res['items']:
        try:
          item_count += 1
          email = item['actor']['email']
          ipAddress = item['ipAddress']
          timedate = item['id']['time']
        
          dRecord = {'email':email, 'ipAddress':ipAddress, 'timedate':timedate}
          #pprint.pprint("%s,\t%s,\t%s\n" % (email, ipAddress,timedate))
          out.write("%s,\t%s,\t%s\n" % (email, ipAddress,timedate))
          #pprint.pprint(dRecord, stream=out)
        
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
          pprint.pprint("ERROR: IOERrror. Bailing", sys.stderr)
          sys.exit(-1)
          
        except KeyboardInterrupt:
          sys.exit(-1)      
  
    #iterated through items in the last RESults
    #get some basics status updates
    try:
      if item_count != 1000:
        a = None  
      else:
        pprint.pprint("Logins Processed = %s" % item_count)
        
      total_count += item_count
      out.close()
      
      #re-initiate the request and populate results
      out = open("/Users/mjw/google_login_audit.csv", "a")      
      req = service.activities().list_next(req, res)
      if req != None:
        res = req.execute()
      else:
        pprint.pprint("****  Done *****")
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
      pprint.pprint("ERROR: IOERrror. Bailing", sys.stderr)
      sys.exit(-1)
      
    except KeyboardInterrupt:
      sys.exit(-1)    

    
    except client.AccessTokenRefreshError:
      print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")  
      
    except:
      traceback.print_exc()  
      
  out.close()
  pprint.pprint("DONE. Total Record count = %s" % total_count)
  

# For more information on the Admin Reports API you can visit:
#
#   https://developers.google.com/admin-sdk/reports/
#
# For more information on the Admin Reports API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/admin/reports_v1/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)
