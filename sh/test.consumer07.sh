#!/bin/sh
topics='^ecg-00[6000-7510]'
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer07.py  "${kafkaIps[1]}:$kafkaPort"  'test07.log' $topics
