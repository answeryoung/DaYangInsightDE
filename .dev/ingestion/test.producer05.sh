#!/bin/sh
topic_indices=0..1999
. ~/sh/anote.cluster.sh
# kafka-topics.sh --create --zookeeper localhost:2181 \
#  --topic $topic --partitions 1 --replication-factor 2
python3 ~/src/test_producer05.py $bucketName 'ecg-data/ecg-{idx_str}.json' \
  "${kafkaIps[2]}:$kafkaPort,${kafkaIps[0]}:$kafkaPort" $topic_indices
