#!/bin/sh
cd ~
echo $PWD
yes | sudo yum install java-1.8.0-openjdk python3.7

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
# export PATH="$PATH:/home/ec2-user/kafka_2.11-2.4.1/bin"

sudo mv /home/ec2-user/kafka_2.11-2.4.1/    /usr/local/kafka
sed -i 's#dataDir=.*#dataDir=/home/ec2-user/kafka#' \
  /usr/local/kafka/config/zookeeper.properties
# defult clientPort=2181 
mkdir /home/ec2-user/zookeeper

# add kafka to PATH
sudo sed -i 's#PATH=.*#PATH=$PATH:/usr/local/kafka/bin:$HOME/.local/bin:$HOME/bin#' \
  /home/ec2-user/.bash_profile
source /home/ec2-user/.bash_profile

# setting up auto-start zookeeper
sudo sed -i '$ a /usr/local/kafka/bin/zookeeper-server-start.sh -daemon \\' /etc/rc.d/rc.local 
sudo sed -i '$ a \  /usr/local/kafka/config/zookeeper.properties' /etc/rc.d/rc.local 

# sudo sed -i '$ a /usr/local/kafka/bin/zookeeper-server-start.sh \\' /etc/rc.d/rc.local 
# sudo sed -i '$ a \  /usr/local/kafka/config/zookeeper.properties \\' /etc/rc.d/rc.local
# sudo sed -i '$ a \  > /dev/null 2>&1 &' /etc/rc.d/rc.local

sudo chmod 733 /etc/rc.d/rc.locall
sudo systemctl enable rc-local
sudo systemctl start rc-local  
  
# write some output to concole
cat /usr/local/kafka/config/zookeeper.properties
echo ""
java -version
scala -version
python3 --version