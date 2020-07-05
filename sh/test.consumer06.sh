#!/bin/sh
topics='^ecg-00[6000-7510]'
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer06.py  "${kafkaIps[1]}:$kafkaPort"  'test06.log' $topics
