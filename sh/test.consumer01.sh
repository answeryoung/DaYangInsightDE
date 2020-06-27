#!/bin/sh
topic='test01'
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer01.py  "${kafkaIps[1]}:$kafkaPort"  'test01c.csv' $topic
