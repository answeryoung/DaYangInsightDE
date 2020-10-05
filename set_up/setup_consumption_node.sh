#!/bin/bash
# setup_consumption_node.sh
# DY200614

cd "$(dirname "$0")"
echo $PWD
. ./anote_cluster.sh
. ./anote_distributions.sh
bash setup_get_dev_tools.sh

python3 -m pip install psycopg2-binary
python3 -m pip install testing.postgresql 
python3 -m pip install scipy