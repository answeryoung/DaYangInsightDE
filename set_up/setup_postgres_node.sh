#!/bin/bash
# setup_postgres_node.sh
# DY200615

cd "$(dirname "$0")"
echo $PWD
. ./anote_cluster.sh
. ./anote_distributions.sh
bash setup_get_dev_tools.sh

echo ""
echo ""
echo "#get postgreSQL"
yes | sudo yum install postgresql postgresql-contrib \
        postgresql-server postgresql-devel postgresql-docs
sleep 1
sudo /usr/bin/postgresql-setup initdb 

echo "Done."
echo "See testingNotes for next steps..."
