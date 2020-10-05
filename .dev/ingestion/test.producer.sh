#!/bin/sh
topic=test
. ~/sh/anote.cluster.sh
kafka-topics.sh --create --zookeeper localhost:2181 \
--topic $topic --partitions 1 --replication-factor 2   
python3 ~/src/test_producer.py $bucketName 'test.csv' \
  "${kafkaIps[0]}:$kafkaPort" $topic
