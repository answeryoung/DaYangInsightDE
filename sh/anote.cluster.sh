#!/bin/sh
# anote.cluster.sh
# DY200614


# zookeeper 
export zookeeperIp="10.0.0.$zkp"
export zookeeperPort=$2181
# kafka broker
declare -A kafkaIps
kafkaIps[0]="10.0.0.$kb0"
kafkaIps[1]="10.0.0.$kb1"
kafkaIps[2]="10.0.0.$kb2"
export kafkaIps
export kafkaPort=$9092
#echo ${kafkaIps[0]} 

# spark master
export sparkMasterIp="10.0.0.$spm"
declare -A sparkWorkerIps
sparkWorkerIps[0]="10.0.0.$sw0"
sparkWorkerIps[1]="10.0.0.$sw1"
sparkWorkerIps[2]="10.0.0.$sw2"
sparkWorkerIps[3]="10.0.0.$sw3"
export sparkWorkerIps

