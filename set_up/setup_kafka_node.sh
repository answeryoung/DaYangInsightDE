#!/bin/bash
# setup_kafka_node.sh
# DY200614
broker_id=$1
#read -p 'Kafka Broker ID [0,1,2]: ' broker_id

cd "$(dirname "$0")"
echo $PWD
. ./anote_cluster.sh
. ./anote_distributions.sh
bash setup_get_dev_tools.sh

echo ""
echo ""
echo "#get kafka"
kafkaHome="$HOME/kafka"   
wget -c --tries=6 $kafka_bin_url -O - | tar -xz
sudo mv kafka_*/ $kafkaHome

echo ""
echo ""
echo "edit server.properties"
log_dir="$HOME/kafka-logs"
mkdir $log_dir

sed -i -e "s/broker.id=.*/broker.id=$broker_id/g" \
  -e '/broker.id=.*/a\broker.rack=AZ1' \
  -e "s#socket.send.buffer.bytes=.*#socket.send.buffer.bytes=524288#" \
  -e "s#socket.receive.buffer.bytes=.*#socket.receive.buffer.bytes=524288#" \
  -e "s#socket.request.max.bytes=.*#socket.request.max.bytes=104857600#" \
  -e '/socket.request.max.bytes=.*/a\queued.max.requests=16' \
  -e '/socket.request.max.bytes=.*/a\fetch.purgatory.purge.interval.requests=100' \
  -e '/socket.request.max.bytes=.*/a\producer.purgatory.purge.interval.requests=100' \
  -e "s#log.dirs=.*#log.dirs=$log_dir#" \
  -e '/offsets.topic.replication.factor=.*/i\offsets.topic.num.partitions=50' \
  -e 's/offsets.topic.replication.factor=.*/offsets.topic.replication.factor=3/g' \
  -e '/transaction.state.log.min.isr=.*/a\min.insync.replicas=1' \
  $kafkaHome/config/server.properties
sed -i -e '/min.insync.replicas=.*/a\default.replication.factor=2' \
  -e 's/log.retention.hours=.*/log.retention.hours=24/g' \
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
  
sudo sed -i '/export PATH/i\PATH=$HOME/kafka/bin:$PATH' \
  $HOME/.bash_profile
cd $HOME
. ./.bash_profile          

echo ""
echo ""
echo "#setting up auto-starting kafka"
sudo sed -i "$ a sudo sh $kafkaHome/bin/kafka-server-start.sh -daemon \
  $kafkaHome/config/server.properties" \
  /etc/rc.d/rc.local
sudo chmod +x /etc/rc.d/rc.local
sudo systemctl enable rc-local
sudo systemctl start rc-local
          
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

# $kafkaHome/bin/kafka-server-start.sh -daemon \
#   $kafkaHome/config/server.properties