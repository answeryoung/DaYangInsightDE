#!/bin/sh
# setup.nodes.PostgreSQL.sh
# DY200615

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh
. ./anote.distributions.sh
sh setup.getDevTools.sh

echo ""
echo ""
echo "#get postgreSQL"
yes | sudo yum install postgresql postgresql-contrib 

  
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
