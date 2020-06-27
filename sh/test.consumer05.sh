#!/bin/sh
topic=ecg-000606
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer05.py  "${kafkaIps[1]}:$kafkaPort"  'test03c.json' $topic
