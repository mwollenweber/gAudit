import argparse
import csv
import socket
import struct
import sys
import logging

from app.database import db
from app import DEBUG

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

ch = logging.StreamHandler()
log.addHandler(ch)


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def main():
    parser = argparse.ArgumentParser(prog='template', usage='%(prog)s [options]')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--version', action='version', version='%(prog)s -1.0')
    parser.add_argument('--debug', '-D', type=bool, dest='DEBUG', default=False)
    parser.add_argument('--infile', '-i', required=True, dest='infile')

    args = parser.parse_args()

    mydb = db()
    mydb.connect()
    mycur = mydb.cur

    reader = csv.reader(open(args.infile, 'rb'), delimiter = ',')
    reader.next() #skip the headerline
    for row in reader:
        try:
            tdstamp = row[0].strip()
            email = row[1].strip().lower()
            username, domain = email.split('@')
            ipstr = row[2].strip()
            ipaddr = ip2int(ipstr)

            query = '''
                REPLACE INTO logins
                (username, domain, ip, event, tdstamp)
                VALUES ('%s', '%s', '%s', 'google audit event', '%s')''' % (username, domain, ipaddr, tdstamp)
            mycur.execute(query)

        except socket.error:
            continue

        except:
            log.exception("Unhandled exception! Handle/Fixme. OMG")
            sys.exit(-1)


if __name__ == "__main__":
    main()
