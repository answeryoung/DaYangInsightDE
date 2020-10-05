#!/bin/bash
# setup_webapp_node.sh
# DY200709

cd "$(dirname "$0")"
echo $PWD
. ./anote_cluster.sh
. ./anote_distributions.sh
bash setup_get_dev_tools.sh

python3 -m pip install psycopg2-binary
python3 -m pip install numpy 
python3 -m pip install pandas  
python3 -m pip install dash
