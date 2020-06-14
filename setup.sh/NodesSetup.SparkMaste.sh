#!/bin/sh
cd ~
echo $PWD

sh getDevTools.sh
sh anoteCluster.sh
# get spark 
wget -c $spark_bin_url -O - | tar -xz

wget https://archive.apache.org/dist/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz
tar xvf spark-2.4.6-bin-hadoop2.6.tgz

sudo mv spark-*/    /usr/local/spark
# add spark to PATH
sparkPath="/usr/local/spark"
sudo sed -i 's#PATH=.*#PATH=$PATH:$sparkPath/bin:$HOME/.local/bin:$HOME/bin#' \
  $HOME/.bash_profile
. $HOME/.bash_profile

# append spark-env.sh
sudo sed -e "$ a \ " \
-e "$ a \
# contents of conf/spark-env.sh \n\
export SPARK_MASTER_HOST=localhost \n\
export JAVA_HOME=$JAVA_HOME \n\
# For PySpark use \n\
export PYSPARK_PYTHON=python3 \n\
# Oversubscription \n\
export SPARK_WORKER_CORES=8" \
  $sparkPath/conf/spark-env.sh.template \
  > $sparkPath/conf/spark-env.sh

sudo sed -e "$ a \ " \
-e "$ a \
# contents of conf/slaves \n\
10.0.0.6 \n\
10.0.0.6 \n\
10.0.0.6 " \
  $sparkPath\conf/slaves.template \
  $sparkPath\conf/slaves.sh

sh $sparkPath/sbin/start-all.sh
