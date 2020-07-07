#!/bin/sh
topics='^ecg-00[5000-5999]'
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer06.py  "${kafkaIps[1]}:$kafkaPort"  'test06.log' $topics
