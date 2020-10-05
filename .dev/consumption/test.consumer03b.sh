#!/bin/sh
topic=test03b
. ~/sh/anote.cluster.sh 
python3  ~/src/test_consumer03.py  "${kafkaIps[1]}:$kafkaPort"  'test03c.json' $topic
