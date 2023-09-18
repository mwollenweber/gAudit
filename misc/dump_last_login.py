#/usr/bin/python

import os
import sys
import traceback
import argparse
import db




def main():
  mydb = db.db(config_file="../server.cfg")
  infilename = sys.argv[1]
  infile = open(infilename, 'r')
  
  for line in infile:
    try:
      netid = line.strip()
      result = mydb.get_last_login(username=netid)
      output = "%s, %s, %s, %s"  % (netid, result[0][1], result[0][2], result[0][3] )
      print output

    except IndexError:
      print "%s,\t,\t,\t," % netid
      
    except:
      traceback.print_exc()    





if __name__ == '__main__':
  main()
