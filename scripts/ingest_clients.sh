#!/bin/bash
source env/bin/activate
export PYTHONPATH=`pwd`:`pwd`/app:$PYTHONPATH

for client in `find ./clients/* -type d -maxdepth 1`
do
    if [[ $client != *"shared"* ]];
    then
        if [[ $client != *"template"* ]];
        then
            pushd $client &> /dev/null;
            echo "UPDATING: " $client;
            python2.7 ingest_google_logins.py
            echo "DONE: " $client;
            popd &> /dev/null;
        fi
    fi
done