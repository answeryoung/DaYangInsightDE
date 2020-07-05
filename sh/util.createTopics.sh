#!/bin/sh
# DY200630

cd "$(dirname "$0")" 
echo $PWD
. ./anote.cluster.sh

topic_head_str="ecg-"
for i in {006000..007510}
    do
        topic=$topic_head_str$i
	kafka-topics.sh --zookeeper $zookeeperIp:$zookeeperPort \
            --create --topic $topic --partitions 1 --replication-factor 3
        echo $topic
done
