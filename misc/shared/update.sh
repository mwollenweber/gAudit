#/usr/bin/bash

#clean old data
python2.7 clean.py
python2.7 ingest_google_logins.py

#this is now done as part of the server functions not per individual client
#python2.7 upload_geo2ip2sql.py -i GeoIPCountryWhois.csv
#python2.7 process_country_codes.py
