#!/bin/sh
. ~/sh/anote.cluster.sh  
python3 ~/src/test_producer02.py $bucketName 'ecg-data-test.json' \
  "${kafkaIps[0]}:$kafkaPort"  8192  