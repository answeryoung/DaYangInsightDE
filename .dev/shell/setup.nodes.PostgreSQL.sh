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

echo "Done."
echo "See testingNotes for next steps..."
