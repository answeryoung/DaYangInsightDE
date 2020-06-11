#!/bin/sh
cd ~
echo $PWD
sudo yum install java-1.8.0-openjdk
sudo yum install python3.7
curl -O https://bootstrap.pypa.io/get-pip.py

wget http://downloads.lightbend.com/scala/2.11.12/scala-2.11.12.rpm
sudo yum -y install scala-2.11.12.rpm

wget https://downloads.apache.org/kafka/2.4.1/kafka_2.11-2.4.1.tgz 
tar -xzf kafka_2.11-2.4.1.tgz

export PATH="$PATH:/home/ec2-user/kafka_2.11-2.4.1/bin"

pip3 install kafka-python