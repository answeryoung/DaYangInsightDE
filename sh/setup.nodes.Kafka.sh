#!/bin/sh
# setup.nodes.Kafka.sh
# DY200614
broker_id=$1
#read -p 'Kafka Broker ID [0,1,2]: ' broker_id

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh
. ./anote.distributions.sh
sh setup.getDevTools.sh

echo ""
echo ""
echo "#get kafka"
kafkaHome="~/kafka"
wget -c --tries=6 $kafka_bin_url -O - | tar -xz
sudo mv kafka_*/ $kafkaHome

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
  -e "s/zookeeper.connect=.*/zookeeper.connect=${zookeeperIp}:${zookeeperPort}/g"  \
  $kafkaHome/config/server.properties    

echo ""
echo ""
echo "#add kafka to PATH"
sudo sed -i -e '/# User specific environment.*/i\if [ -f ~/sh/anote.cluster.sh ]; then' \
  -e '/# User specific environment.*/i\        . ~/sh/anote.cluster.sh' \
  -e '/# User specific environment.*/i\fi' \
  $HOME/.bash_profile
  
sudo sed -i "$ a \
  alias cdKafka='cd $kafkaHome/'" \
  $HOME/.bashrc
  
sudo sed -i '/export PATH/i\PATH=/usr/local/kafka/bin:$PATH' \
  $HOME/.bash_profile
cd $HOME
. ./.bash_profile

# echo ""
# echo ""
# echo "#setting up auto-starting kafka"
# sudo sed -i "$ a sudo sh $kafkaHome/bin/kafka-server-start.sh -daemon \
#   $kafkaHome/config/server.properties" \
#   /etc/rc.d/rc.local
# sudo chmod +x /etc/rc.d/rc.local
# sudo systemctl enable rc-local
# sudo systemctl start rc-local

# write some output to concole
echo ""
echo ""
echo ""
echo ""
java -version
scala -version
sed -n -e '/broker.id=.*/p' -e '/zookeeper.connect=.*/p' \
  $kafkaHome/config/server.properties 
echo $PATH
echo ""
echo $JAVA_HOME

$kafkaHome/bin/kafka-server-start.sh -daemon \
  $kafkaHome/config/server.properties