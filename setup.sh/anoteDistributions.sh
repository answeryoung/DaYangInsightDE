#!/bin/sh
# anoteDistributions.sh
# DY200614

# Check available versions
# $sudo yum list | grep openjdk
java_dist=java-1.8.0-openjdk.x86_64
javaHome="/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.amzn2.0.1.x86_64/jre"
# $file $(which java)
# /usr/bin/java: symbolic link to `/etc/alternatives/java'
# $file /etc/alternatives/java
# /etc/alternatives/java: symbolic link to `/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.amzn2.0.1.x86_64/jre/bin/java'
# $javaHome="/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.amzn2.0.1.x86_64/jre"
# THIS IS HOW TO FIND JAVA_HOME (already set in setDistributionNames.sh)
# WHICH NEEDS UPDATE!!

# $sudo yum list | grep python3
python3_dist=python3

# It's a good idea to make sure scala versions are consistent.
scala_bin_url="http://downloads.lightbend.com/scala/2.11.12/scala-2.11.12.rpm"
# make sure the following are .tgz files
kafka_bin_url="https://downloads.apache.org/kafka/2.4.1/kafka_2.11-2.4.1.tgz"
spark_bin_url="https://archive.apache.org/dist/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz"
