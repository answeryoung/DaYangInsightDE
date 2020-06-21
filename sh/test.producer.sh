#!/bin/sh
. ~/sh/anote.cluster.sh  
python3 ~/src/test_producer.py $bucketName 'test.csv' \
  "${kafkaIps[0]}:$kafkaPort" 'test'