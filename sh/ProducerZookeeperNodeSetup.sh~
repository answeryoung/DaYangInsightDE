#!/bin/sh
cd ~
echo $PWD
yes | sudo yum install java-1.8.0-openjdk
yes | sudo yum install python3.7

# get scala_2.11
yes | wget http://downloads.lightbend.com/scala/2.11.12/scala-2.11.12.rpm
sudo yum -y install scala-2.11.12.rpm

# get kafka-python and babo3
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
pip3 install kafka-python
pip3 install boto3

# get kafka_2.4.1
yes | wget https://downloads.apache.org/kafka/2.4.1/kafka_2.11-2.4.1.tgz 
tar -xzf kafka_2.11-2.4.1.tgz
export PATH="$PATH:/home/ec2-user/kafka_2.11-2.4.1/bin"

python3 