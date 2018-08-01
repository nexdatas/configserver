#!/usr/bin/env bash

if [ $1 = "2" ]; then
    echo "run python-nxsconfigserver"
    docker exec -it ndts python test/runtest.py
else
    echo "run python3-nxsconfigserver"
    docker exec -it ndts python3 test/runtest.py
fi    
if [ $? -ne "0" ]
then
    exit -1
fi
