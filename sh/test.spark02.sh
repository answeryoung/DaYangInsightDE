#!/bin/sh
# setup.nodes.Kafka.sh
# DY200616

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh

# It is important not to leave any spaces between packages
spark-submit --packages \
org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.6\
org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 ~/src/test_spark.py