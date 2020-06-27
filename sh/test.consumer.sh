#!/bin/sh
topic='test'
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer.py  "${kafkaIps[1]}:$kafkaPort"  'test_c.csv' $topic
