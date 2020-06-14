#!/bin/sh
# setup.nodes.Kafka.sh
# DY200614

read -p 'Kafka Broker ID [0,1,2]: ' broker_id

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh
. ./anote.distributions.sh
sh setup.getDevTools.sh

echo ""
echo ""
echo "get kafka"
kafkaHome="/usr/local/kafka"
mkdir $kafkaHome
wget -c $kafka_bin_url -O - | tar -xz $kafkaHome

echo ""
echo ""
echo "edit server.properties"
log_dir="$HOME/kafka-logs"
mkdir $log_dir

sed -i -e "s/broker.id=.*/broker.id=$broker_id/g" \
  -e '/broker.id=.*/a\broker.rack=AZ1' \
  -e "s#log.dirs=.*#log.dirs=$log_dir#" \
  -e '/offsets.topic.replication.factor=.*/i\offsets.topic.num.partitions=3' \
  -e 's/offsets.topic.replication.factor=.*/offsets.topic.replication.factor=2/g' \
  -e '/transaction.state.log.min.isr=.*/a\min.insync.replicas=2' \
  $kafkaHome/config/server.properties
sed -i -e '/min.insync.replicas=.*/a\default.replication.factor=2' \ 
  -e 's/log.retention.hours=.*/log.retention.hours=4/g' \
  -e "s/zookeeper.connect=.*/zookeeper.connect=$zookeeperIp:$zookeeperPort/g" \
  $kafkaHome/config/server.properties                                                                                                                                                                

# add kafka to PATH
sudo sed -i 's#PATH=.*#PATH=$PATH:/usr/local/kafka/bin:$HOME/.local/bin:$HOME/bin#' \
  $HOME/.bash_profile
. $HOME/.bash_profile

# setting up auto-start kafka
sudo sed -i "$ a $kafkaHome/bin/kafka-server-start.sh -daemon \\\ \n\
  $kafkaHome/config/server.properties" \
  /etc/rc.d/rc.local
sudo chmod +x /etc/rc.d/rc.local
sudo systemctl enable rc-local
sudo systemctl start rc-local

# write some output to concole
echo ""
java -version
scala -version
sed -n -e '/broker.id=.*/p' -e '/zookeeper.connect=.*/p' \
  $kafkaHome/config/server.properties 
echo $PATH
echo $JAVA_HOME