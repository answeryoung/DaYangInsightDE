#!/bin/sh
# setup.getDevTools.sh
# java python3 scala
# pip sbt
# DY200614

cd "$(dirname "$0")"
echo $PWD
# source from anote.distributions.sh 
#. ./anote.distributions.sh

echo ""
echo ""
echo '#get "Development Tools"'
sleep 1
yes | sudo yum groupinstall "Development Tools"

echo ""
echo ""
echo "#get java and python3"
sleep 1
yes | sudo yum install $java_dist $python3_dist 

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
sudo sed -i -e "/export PATH/i\JAVA_HOME=\"$javaHome\"" \
  -e '/export PATH/i\PATH=$JAVA_HOME/bin:$PATH' \
  -e '/export PATH/i\ ' \
  $HOME/.bash_profile
# cd $HOME
# . ./.bash_profile

echo ""
echo ""
echo "#get scala"
sleep 1
yes | sudo rpm -i $scala_bin_url

echo ""
echo ""
echo "#setup pip"
sleep 1
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py  

echo ""
echo ""
echo "#setup sbt"
sleep 1
curl https://bintray.com/sbt/rpm/rpm | sudo tee /etc/yum.repos.d/bintray-sbt-rpm.repo
yes | sudo yum install sbt 
