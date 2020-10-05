#!/bin/bash
# copy to anote_cluster.sh
# fill in the values according to your set-up
# DY200621

# bucket
export bucketName='dashtenn-insightde-02'

# zookeeper
export zookeeperIp="10.0.0.6"
export zookeeperPort=2181 # the default 2181
# kafka broker
declare -A kafkaIps
kafkaIps[0]="10.0.0.7"
kafkaIps[1]="10.0.0.8"
kafkaIps[2]="10.0.0.9"
export kafkaIps
export kafkaPort=9092 # the default 9092
#echo ${kafkaIps[0]}

# spark cluster
export sparkMasterIp="10.0.0.10"
declare -A sparkWorkerIps
sparkWorkerIps[0]="10.0.0.11"
sparkWorkerIps[1]="10.0.0.12"
sparkWorkerIps[2]="10.0.0.13"
sparkWorkerIps[3]="10.0.0.14"
export sparkWorkerIps

# postgreSQL
export psqlIp="10.0.0.4"
export psqlPort=5432 # the default 5432
export dbName='insightde' # need to use lower case
export db_super_user='dy'
export db_su_pwd='66666666'

# dash App
export app_host='ec2-54-189-36-235.us-west-2.compute.amazonaws.com'
export app_port=8080

