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
yes | sudo yum install postgresql postgresql-contrib \
        postgresql-server postgresql-devel postgresql-docs
sleep 1
sudo /usr/bin/postgresql-setup initdb 


sudo -u postgres -i 
pqsl

echo ""
echo ""
echo "As the superuser and configure pgsql"
echo ""
echo '$sudo su'
echo '$cd /var/lib/pgsql/data'
echo ""
echo "Then, edit pg_hba.conf and "

sudo systemctl enable postgresql
sudo systemctl start postgresql

sudo -u postgres -i  
CREATE USER power_user SUPERUSER;
ALTER USER power_user WITH PASSWORD '66666666';
CREATE USER other_user NOSUPERUSER;
ALTER USER other_user WITH PASSWORD '66666666';
CREATE USER storageloader PASSWORD '66666666';
CREATE DATABASE snowplow WITH OWNER other_user;
\du+
\q

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
