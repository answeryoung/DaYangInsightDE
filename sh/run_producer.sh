#!/bin/bash

topic_indices=6000..7510

. ~/sh/anote_cluster.sh

python3 ~/src/ingestion.py $bucketName 'ecg/ecg-{idx_str}.json' \
  "${kafkaIps[2]}:$kafkaPort,${kafkaIps[0]}:$kafkaPort" $topic_indices
