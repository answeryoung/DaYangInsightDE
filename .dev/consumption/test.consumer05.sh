#!/bin/sh
topic=ecg-006051
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer05.py  "${kafkaIps[1]}:$kafkaPort"  'test05c.json' $topic
