#/usr/bin/python

import os
import sys
import traceback
import argparse
from netaddr import IPNetwork



def main(argv):
  parser = argparse.ArgumentParser(prog='dump_google_drive', usage='%(prog)s [options]')
  parser.add_argument('--infile', '-i', type=str, dest='infilename', required=True)
  args = parser.parse_args()  
  
  try:
    infile = open(args.infilename, "r")
    for line in infile:
      cidr = line.strip()
      
      if line.find("#") >= 0:
        continue
      
      if len(line) < 6:
        continue
      
      #is probably just an ip
      if line.find("/") <5:
        print line
        
      for ip in IPNetwork(cidr):
        print '%s' % ip
        
  except:
    traceback.print_exc()
    #continue

if __name__ == '__main__':
  main(sys.argv)
