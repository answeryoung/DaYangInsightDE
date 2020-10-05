#!/bin/bash

topics='^ecg-00[6000-7510]'

. ~/sh/anote_cluster.sh 

python3  ~/src/consumption.py  \
    "${kafkaIps[1]}:$kafkaPort"  'consumption.log' $topics
