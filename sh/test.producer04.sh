#!/bin/sh
topic=test
. ~/sh/anote.cluster.sh
kafka-topics.sh --create --zookeeper localhost:2181 \
  --topic $topic --partitions 4 --replication-factor 3
python3 ~/src/test_producer03.py $bucketName 'ecg-data-test.json' \
  "${kafkaIps[2]}:$kafkaPort" $topic
