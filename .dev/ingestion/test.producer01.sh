#!/bin/sh
topic=test01
. ~/sh/anote.cluster.sh
kafka-topics.sh --create --zookeeper localhost:2181 \
--topic $topic --partitions 1 --replication-factor 2
python3 ~/src/test_producer.py $bucketName 'test1.csv' \
  "${kafkaIps[1]}:$kafkaPort" $topic
