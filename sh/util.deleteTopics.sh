#!/bin/sh
# DY200623

cd "$(dirname "$0")" 
echo $PWD
. ./anote.cluster.sh

topic_head_str="ecg-"
for i in {000000..007511}
    do
        topic=$topic_head_str$i
	kafka-topics.sh --zookeeper $zookeeperIp:$zookeeperPort \
            --delete --topic $topic
        echo $topic
done
