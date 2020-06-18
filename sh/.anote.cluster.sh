#!/bin/sh
# copy to anote.cluster.sh 
# and fill in (replace the values with) according to your cluster setup
# DY200614

# zookeeper 
export zookeeperIp="10.0.0.6"
export zookeeperPort=2181 # the default is 2181

# kafka broker
declare -A kafkaIps
kafkaIps[0]="0.0.0.0"
kafkaIps[1]="0.0.0.0"
kafkaIps[2]="0.0.0.0"
export kafkaIps
export kafkaPort=0000 # the default is 9092
#echo ${kafkaIps[0]} 

# spark cluster
export sparkMasterIp="0.0.0.0"
declare -A sparkWorkerIps
sparkWorkerIps[0]="0.0.0.0"
sparkWorkerIps[1]="0.0.0.0"
sparkWorkerIps[2]="0.0.0.0"
sparkWorkerIps[3]="0.0.0.0"
export sparkWorkerIps

# postgreSQL
export psqlIp="0.0.0.0"
export psqlPort=0000 # the default is 5432