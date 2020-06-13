#!/bin/sh
cd ~
echo $PWD
yes | sudo yum install java-1.8.0-openjdk python3.7

# get scala_2.11
wget http://downloads.lightbend.com/scala/2.11.12/scala-2.11.12.rpm
sudo yum -y install scala-2.11.12.rpm

# get spark 
wget https://archive.apache.org/dist/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz
tar xvf spark-2.4.6-bin-hadoop2.6.tgz
sudo mv spark-2.4.6-bin-hadoop2.6/ /usr/local/spark
export PATH="/usr/local/spark:$PATH"
source ~/.profile

cp /usr/local/spark/conf/spark-env.sh.template /usr/local/spark/conf/spark-env.sh
{
    echo ''    
	echo '# contents of conf/spark-env.sh'
    echo 'export SPARK_MASTER_HOST=10.0.0.6'
    echo 'export JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk'
    echo '# For PySpark use'
    echo 'export PYSPARK_PYTHON=python3'
    echo '# Oversubscription'
    echo 'export SPARK_WORKER_CORES=6'
    echo ''
} >> /usr/local/spark/conf/spark-env.sh

cp /usr/local/spark/conf/slaves.template /usr/local/spark/conf/slaves
{
    echo ''    
	echo '# contents of conf/slaves'
    echo '10.0.0.6'
    echo '10.0.0.6'
    echo '10.0.0.6'
    echo ''
} >> /usr/local/spark/conf/slaves

sh spark-2.4.6-bin-without-hadoop/sbin/start-all.sh

# get kafka-python and babo3
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
jre-1.8.0-openjdk-1.8.0.252.b09-2.amzn2.0.1.x86_64