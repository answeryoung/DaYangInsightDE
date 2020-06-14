#!/bin/sh
# anoteCluster.sh
# DY200614

# zookeeper 
zookeeperIp="10.0.0.4"
zookeeperPort=2181
# kafka broker
declare -A kafkaIps
kafkaIps[0]="10.0.0.1"
kafkaIps[1]="10.0.0.2"
kafkaIps[2]="10.0.0.3"
kafkaPort=9092

# spark master
sparkMasterIp="10.0.0.0"



