#!/bin/sh
# setup.nodes.SparkWorker.sh
# DY200614

cd "$(dirname "$0")"
echo $PWD
. ./anote.cluster.sh
. ./anote.distributions.sh
sh setup.getDevTools.sh

echo ""
echo ""
echo "#get spark"
sparkHome="/usr/local/spark"
wget -c --tries=6 $spark_bin_url -O - | tar -xz
sudo mv spark-*/ $sparkHome

echo ""
echo ""
echo "#add spark to PATH"
sudo sed -i "$ a \
  alias cdSpark='cd $sparkHome/'" \
  $HOME/.bashrc
. ./.bashrc
sudo sed -i '/export PATH/i\PATH=/usr/local/spark/bin:$PATH' \
  $HOME/.bash_profile
cd $HOME
. ./.bash_profile

echo "# openssh: you should already have this"
sudo yum install -y openssh

echo ""
echo ""
echo "#append to spark-env.sh"
sudo sed -e "$ a \ " \
-e "$ a \
# contents of conf/spark-env.sh \n\
export SPARK_MASTER_HOST=$sparkMasterIp \n\
export JAVA_HOME=$JAVA_HOME \n\
# For PySpark use \n\
export PYSPARK_PYTHON=python3 \n\
# Oversubscription \n\
export SPARK_WORKER_CORES=8" \
  $sparkHome/conf/spark-env.sh.template \
  > $sparkHome/conf/spark-env.sh

echo "# append to slave"
sudo sed -e "$ a \ " \
-e "$ a \
# contents of conf/slaves \n\
${sparkWorkerIps[0]} \n\
${sparkWorkerIps[1]} \n\
${sparkWorkerIps[2]} \n\
${sparkWorkerIps[3]} " \
  $sparkHome/conf/slaves.template \
  > $sparkHome/conf/slaves

echo ""
echo ""
echo "#setting up auto-starting spark cluster"
sudo sed -i "$ a # sh $sparkHome/sbin/start-all.sh" \
  /etc/rc.d/rc.local
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
echo $PATH
echo ""
echo $JAVA_HOME

# sleep 5
# sudo systemctl start rc-local