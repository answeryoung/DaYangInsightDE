#!/bin/sh
topic=test03c
. ~/sh/anote.cluster.sh
# kafka-topics.sh --create --zookeeper localhost:2181 \
#   --topic $topic --partitions 3 --replication-factor 2
python3 ~/src/test_producer03.py $bucketName 'ecg-data-s.json' \
  "${kafkaIps[0]}:$kafkaPort,${kafkaIps[2]}:$kafkaPort" $topic
