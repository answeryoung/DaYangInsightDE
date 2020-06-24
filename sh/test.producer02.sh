#!/bin/sh
topic=test02
. ~/sh/anote.cluster.sh
kafka-topics.sh --create --zookeeper localhost:2181 \
  --topic $topic --partitions 3 --replication-factor 2
python3 ~/src/test_producer02.py $bucketName 'ecg-data-g500.json' \
  "${kafkaIps[2]}:$kafkaPort" $topic
