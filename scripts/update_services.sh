#!/bin/bash
source env/bin/activate
export PYTHONPATH=`pwd`:`pwd`/app:$PYTHONPATH

for service in `find ./app/services/* -type d -maxdepth 1`
do
    echo $service
    pushd $service &> /dev/null
    python2.7 models.py
    popd  &> /dev/null
done