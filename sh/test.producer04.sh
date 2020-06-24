#!/bin/sh
topic=test04
. ~/sh/anote.cluster.sh
# kafka-topics.sh --create --zookeeper localhost:2181 \
#  --topic $topic --partitions 1 --replication-factor 2
python3 ~/src/test_producer04.py $bucketName 'ecg-data-s.json' \
  "${kafkaIps[2]}:$kafkaPort" $topic
