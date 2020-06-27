#!/bin/sh
topics='^ecg-0000[00-11]'
. ~/sh/anote.cluster.sh
python3  ~/src/test_consumer06.py  "${kafkaIps[1]}:$kafkaPort"  'test06.log' $topics
