#!/bin/sh
# setup.nodes.Preprocessing.sh
# DY200615

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh
. ./anote.distributions.sh
sh setup.getDevTools.sh

echo ""
echo ""
echo "#get kafka-python and babo3"
pip3 install kafka-python 
pip3 install boto3 # for interfacing with aws s3
pip3 install wfdb # for using PhysioBank data (specific to this project)
  
# write some output to concole
echo ""
echo ""
echo ""
echo ""
java -version
scala -version
python3 --version
echo $PATH
echo ""
echo $JAVA_HOME
