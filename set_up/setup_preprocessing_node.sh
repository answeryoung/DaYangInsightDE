#!/bin/sh
# setup_preprocessing_node.sh
# DY200615

cd "$(dirname "$0")"
echo $PWD
. ./anote_cluster.sh
. ./anote_distributions.sh
bash setup_get_dev_tools.sh

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
