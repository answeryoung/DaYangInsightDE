#!/bin/sh
# setup.getDevTools.sh
# java python3 scala
# pip sbt
# DY200615
# NOT END-TO-END TESTED

cd "$(dirname "$0")"
echo $PWD
# source from anote.distributions.sh 
source anote.distributions.sh

echo ""
echo ""
echo '#get "build-essential"'
sleep 1
yes | sudo apt-get install build-essential

echo ""
echo ""
echo "#get java and python3"
sleep 1
yes | sudo apt-get install $java_dist_ubuntu $python3_dist 

echo ""
echo ""
echo "#set JAVA_HOME"
sleep 1
# $file $(which java)
# /usr/bin/java: symbolic link to `/etc/alternatives/java'
# $file /etc/alternatives/java
# /etc/alternatives/java: symbolic link to `/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.amzn2.0.1.x86_64/jre/bin/java'
# $javaHome="/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.amzn2.0.1.x86_64/jre"
# THIS IS HOW TO FIND JAVA_HOME (already set in setDistributionNames.sh)
# WHICH NEEDS UPDATE!!
sudo sed -i -e "/export PATH/i\JAVA_HOME=\"$javaHome_ubuntu\"" \
  -e '/export PATH/i\PATH=$JAVA_HOME/bin:$PATH' \
  -e '/export PATH/i\ ' \
  $HOME/.bash_profile
# cd $HOME
# . ./.bash_profile

echo ""
echo ""
echo "#get scala"
sleep 1
wget --output-document=temp.deb $scala_bin_url_ubuntu | sudo dpkg --install temp.deb

echo ""
echo ""
echo "#setup pip"
sleep 1
yes | sudo apt install python3-pip

echo ""
echo ""
echo "#setup sbt"
sleep 1
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get install sbt
