#!/bin/bash

printf "creating database. You will be prompted for your mysql password\n"
mysql -u root -p < gaudit.sql 
python2.7 upload_geo2ip2sql.py  -i GeoIPCountryWhois.csv 

./update.sh

