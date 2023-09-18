import argparse
import httplib2
import sys
import traceback
import gdata.apps.audit.service

from urllib2 import HTTPError
from oauth2client import file

from app.auth.models import User
from app.main.auditModel import gdata, emailExportAuditModel
from app.database import db_session, engine, Base
from app import db, DEBUG


def main(argv):
    parser = argparse.ArgumentParser(description='Update the login events for a domain')
    parser.add_argument('--domain', type=str, required=True, help="You must specific the domain to update")
    args = parser.parse_args(argv)
    mydomain = args.domain

    gauth = User().getGoogleAuthByDomain(domain=mydomain)
    if gauth is None:
        print "ERROR: Unable to find google auth for domain=%s\nExiting!" % args.domain
        sys.exit(-1)

    credentials = file.Credentials().new_from_json(gauth)
    http = httplib2.Http()
    http = credentials.authorize(http)

    audit_service = gdata.apps.audit.service.AuditService(domain=mydomain)
    auth_headers = {u'Authorization': u'Bearer %s' % credentials.access_token}
    audit_service.additional_headers = auth_headers

    myEmailAudits = emailExportAuditModel(mydomain, mydomain, GoogleDriveRootName="gAuditExports")
    myEmailAudits.updateAudits()
    myEmailAudits.printAllExportRequestStatus()
    db_session.flush()
    db_session.commit()

    for d in myEmailAudits.listAvailableDownloads():
        print "FIXME: auditModel Main don't  write the fucking download logic here"
        try:
            myEmailAudits.exportFilesToGoogle(d)

        except HTTPError:
            traceback.print_exc(file=sys.stderr)
            print("ERROR: Exiting")
            sys.exit(-1)

        except KeyboardInterrupt:
            print "KeyboardInterrupt! Exiting"
            db_session.rollback()
            db_session.flush()
            sys.exit(0)

        except SystemExit:
            sys.exit(0)

    db_session.flush()
    db_session.commit()
    db_session.close()

    print "Finis"


if __name__ == '__main__':
    main(sys.argv[1:])
