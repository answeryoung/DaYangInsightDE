#!/bin/sh
# setup.nodes.ProducerZookeeper.sh
# DY200614

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh
. ./anote.distributions.sh
sh setup.getDevTools.sh

echo ""
echo ""
echo "#get kafka"
sleep 1
kafkaHome="/usr/local/kafka"
wget -c $kafka_bin_url -O - | tar -xz
sudo mv kafka_*/ $kafkaHome

echo ""
echo ""
echo "#edit zookeeper.properties"
data_dir="$HOME/zookeeper-data"
mkdir $data_dir

sed -i "s#dataDir=.*#dataDir=$data_dir#" \
  $kafkaHome/config/zookeeper.properties

echo ""
echo ""
echo "#add kafka to PATH"
sudo sed -i 's#PATH=.*#PATH=$PATH:/usr/local/kafka/bin:$HOME/.local/bin:$HOME/bin#,0' \
  $HOME/.bash_profile
cd $HOME
. ./.bash_profile

echo ""
echo ""
echo "#get kafka-python and babo3"
pip3 install kafka-python
pip3 install boto3

echo ""
echo ""
echo "#setting up auto-starting zookeeper"
sudo sed -i "$ a $kafkaHome/bin/zookeeper-server-start.sh -daemon \
  $kafkaHome/config/zookeeper.properties" \
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
python3 --version
sed -n '/dataDir=.*/p' $kafkaHome/config/zookeeper.properties
echo $PATH
echo ""
echo $JAVA_HOME
