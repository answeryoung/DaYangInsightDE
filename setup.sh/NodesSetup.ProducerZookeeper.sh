#!/bin/sh
# NodesSetup.ProducerZookeeper.sh
# DY200614

cd ~
echo $PWD
sh getDevTools.sh
sh anoteCluster.sh

# get kafka
kafkaHome="/usr/local/kafka"
mkdir $kafkaHome
wget -c $kafka_bin_url -O - | tar -xz $kafkaHome

# edit zookeeper.properties
data_dir="$HOME/zookeeper-data"
mkdir $data_dir

sed -i "s#dataDir=.*#dataDir=$data_dir" \
  $zkpr_prop

# add kafka to PATH
sudo sed -i 's#PATH=.*#PATH=$PATH:/usr/local/kafka/bin:$HOME/.local/bin:$HOME/bin#' \
  $HOME/.bash_profile
. $HOME/.bash_profile

# get kafka-python and babo3
pip3 install kafka-python
pip3 install boto3

# setting up auto-start zookeeper
sudo sed -i "$ a $kafkaHome/bin/zookeeper-server-start.sh -daemon \\\ \n\
  $kafkaHome/config/zookeeper.properties" /etc/rc.d/rc.local
sudo chmod +x /etc/rc.d/rc.locall
sudo systemctl enable rc-local
sudo systemctl start rc-local
  
# write some output to concole
echo ""
java -version
scala -version
python3 --version
sed -n 'dataDir=.*/p' $zkpr_prop
echo $PATH
echo $JAVA_HOME
