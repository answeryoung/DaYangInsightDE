#!/bin/sh
# NodesSetup.SparkMaster.sh
# DY200614

cd "$(dirname "$0")"
echo $PWD
sh getDevTools.sh
sh anoteCluster.sh

# get spark
sparkHome="/usr/local/spark"
mkdir $sparkHome 
wget -c $spark_bin_url -O - | tar -xz $sparkHome

# append to spark-env.sh
sudo sed -e "$ a \ " \
-e "$ a \
# contents of conf/spark-env.sh \n\
export SPARK_MASTER_HOST=localhost \n\
export JAVA_HOME=$JAVA_HOME \n\
# For PySpark use \n\
export PYSPARK_PYTHON=python3 \n\
# Oversubscription \n\
export SPARK_WORKER_CORES=8" \
  $sparkHome/conf/spark-env.sh.template \
  > $sparkHome/conf/spark-env.sh

# append to slave
cp $sparkPath\conf/slaves.template    $sparkPath\conf/slaves

sudo sed -e "$ a \ " \
-e "$ a \
# contents of conf/slaves \n\
10.0.0.6 \n\
10.0.0.6 \n\
10.0.0.6 " \
  $sparkPath\conf/slaves.template \
  $sparkPath\conf/slaves

# add spark to PATH
sparkPath="/usr/local/spark"
sudo sed -i 's#PATH=.*#PATH=$PATH:$sparkPath/bin:$HOME/.local/bin:$HOME/bin#' \
  $HOME/.bash_profile
. $HOME/.bash_profile




sh $sparkPath/sbin/start-all.sh
